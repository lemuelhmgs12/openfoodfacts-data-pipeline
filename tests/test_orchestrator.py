import json,pytest
from pipeline.api_client import OpenFoodFactsClient, TransientAPIError
from pipeline.orchestrator import run
from datetime import date
from botocore.exceptions import ClientError

def test_run_happy_path(fake_s3, fake_products_four, settings, mocker):
    mocker.patch.object(OpenFoodFactsClient, "iter_products", return_value=fake_products_four)

    run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 3

    data = json.loads(fake_s3.storage[settings.watermark_key])
    assert data["last_modified_t"] == 500


def test_leftover_partial_batch_processed(fake_s3, settings, mocker):

    fake_product = [
        {"code": "111", "product_name": "Fake Chips", "last_modified_t": 500},
        {"code": "222", "product_name": "Fake Cookies", "last_modified_t": 400},
        {"code": "333", "product_name": "Fake Crackers", "last_modified_t": 300},
    ]

    mocker.patch.object(OpenFoodFactsClient,"iter_products", return_value= fake_product)

    run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 3

    data = json.loads(fake_s3.storage[settings.watermark_key])
    assert data["last_modified_t"] == 500

    leftover_key = f"{settings.raw_prefix}/ingest_date={date.today().isoformat()}/batch_001.json"
    leftover_batch = json.loads(fake_s3.storage[leftover_key])

    assert leftover_batch == [{"code": "333", "product_name": "Fake Crackers", "last_modified_t": 300}]
    
    

def test_openfoodfacts_error_propagates(fake_s3, settings, mocker):
    mocker.patch.object(OpenFoodFactsClient, "iter_products", side_effect=TransientAPIError())

    with pytest.raises(TransientAPIError):
        run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 0

def test_watermark_not_written_after_partial_batch_failure(fake_s3, fake_products_four, settings, mocker):
    mocker.patch.object(OpenFoodFactsClient, "iter_products", return_value=fake_products_four)

    call_count = [0]
    def flaky_put_object(Bucket, Key, Body):
        call_count[0] +=1
        if call_count[0] == 1:
            fake_s3.storage[Key] = Body
        else:
            raise ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "nope"}},
                "PutObject",)
        
    mocker.patch.object(fake_s3, "put_object", side_effect=flaky_put_object)

    with pytest.raises(ClientError):
        run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 1
    assert settings.watermark_key not in fake_s3.storage

def test_client_error_on_first_write_writes_nothing(fake_s3, fake_products_four, settings, mocker):
    mocker.patch.object(OpenFoodFactsClient, "iter_products", return_value=fake_products_four)
    mocker.patch.object(fake_s3, "put_object", side_effect=ClientError({"Error": {"Code": "AccessDenied", "Message": "nope"}},
    "PutObject",))

    with pytest.raises(ClientError):
        run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 0


def test_generic_exception_propagates(fake_s3, fake_products_four, settings, mocker):
    mocker.patch.object (OpenFoodFactsClient, "iter_products", side_effect=TypeError("Unexpected error!"))
    

    with pytest.raises(TypeError):
        run(settings, s3_client=fake_s3)

    assert len(fake_s3.storage) == 0