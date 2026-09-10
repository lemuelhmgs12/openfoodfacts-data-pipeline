import pytest
import requests,responses
from pipeline.config import Settings
from pipeline.api_client import OpenFoodFactsClient,TransientAPIError,OpenFoodFactsError

URL = f"{Settings.base_url}/api/v2/search"

@pytest.fixture
def settings():
    return Settings(
        max_retry_attempts=3,
        backoff_multiplier= 1,
        backoff_min_seconds = 1,
        backoff_max_seconds = 2,

    )

@pytest.fixture
def client(settings):
    return OpenFoodFactsClient(settings=settings)


@responses.activate
def test_503_exhausts_retries_and_raises(client):
    for _ in range(3):
        responses.add(responses.GET, URL, status=503)

    with pytest.raises(TransientAPIError):
        client._fetch_page(1)



@responses.activate
def test_400_bad_request_noretry(client):
    responses.add(responses.GET, URL, status=400)

    with pytest.raises(OpenFoodFactsError):
        client._fetch_page(1)

@responses.activate
def test_network_error_is_retried_then_exhausts(client):
    for _ in range(3):
        responses.add(responses.GET, URL, body=requests.exceptions.ConnectionError())

    with pytest.raises(TransientAPIError):
        client._fetch_page(1)

@responses.activate
def test_success_returns_parsed_data(client):
    fake_product_data = {"count": 1,
    "page": 1,
    "page_size": 100,
    "products": [
        {
            "code": "1234567890123",
            "product_name": "Fake Snack Bar",
            "last_modified_t": 1788309134,
        }
    ],}
    responses.add(responses.GET, URL, status=200, json=fake_product_data)

    result = client._fetch_page(1)

    assert result == fake_product_data

def test_happy_path_walk_two_pages_stop_on_third_empty(client, mocker):
    mock_fetch = mocker.patch.object(client, "_fetch_page", side_effect=[
    {
        "count": 2,
        "products": [
            {"code": "111", "product_name": "Fake Chips", "last_modified_t": 500},
            {"code": "222", "product_name": "Fake Cookies", "last_modified_t": 400},
        ],
    },
    {
        "count": 1,
        "products": [
            {"code": "333", "product_name": "Fake Crackers", "last_modified_t": 300},
        ],
    },
    {
        "count": 0,
        "products": [],
    },
    ])
    result = list(client.iter_products())

    assert len(result) == 3

    assert [p['code'] for p in result] == ['111','222','333']

    assert mock_fetch.call_count == 3


def test_iter_products_stops_at_watermark(client, mocker):
    mock_fetch = mocker.patch.object(client, "_fetch_page", side_effect=[
    {
        "count": 2,
        "products": [
            {"code": "111", "product_name": "Fake A", "last_modified_t": 500},
            {"code": "222", "product_name": "Fake B", "last_modified_t": 400},
        ],
    },
    {
        "count": 2,
        "products": [
            {"code": "333", "product_name": "Fake C", "last_modified_t": 300},
            {"code": "444", "product_name": "Fake D", "last_modified_t": 200},  
        ],
    },
    {
        "count": 1,
        "products": [
            {"code": "555", "product_name": "Fake E", "last_modified_t": 100},  
        ],
    },
    ])

    result = list(client.iter_products(250))

    assert len(result) == 3

    assert [p['code'] for p in result] == ['111','222','333']

    assert mock_fetch.call_count == 2