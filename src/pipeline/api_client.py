import requests
from tenacity import Retrying, stop_after_attempt, wait_exponential, retry_if_exception_type
from collections.abc import Iterator
import logging

logger = logging.getLogger(__name__)

class OpenFoodFactsError(Exception):
    """Base error for anything from this API. Not retried"""
    pass

class TransientAPIError(OpenFoodFactsError):
    """Retriable failures: 5xx responses, network-level errors."""
    pass

class OpenFoodFactsClient:
    def __init__(self, settings, session=None):
        self.settings = settings
        self.session = session if session is not None else requests.Session()
        self.session.headers['User-Agent'] = self.settings.user_agent



 

    def _fetch_page_once(self, page: int):
        params = {
        "categories_tags": self.settings.category,
        "sort_by": "last_modified_t",
        "page": page,
        "page_size": self.settings.page_size,
        "fields": ",".join(self.settings.fields)
        }

        try:
            response = self.session.get(f"{self.settings.base_url}/api/v2/search", params=params, timeout = self.settings.timeout)
        except requests.exceptions.RequestException as exc:
            raise TransientAPIError (f"request failed on page {page}: {exc}") from exc

        if(500 <= response.status_code < 600):
            logger.error(f"{response.status_code} thrown by API. Retring....page: {page}")
            raise TransientAPIError(f"{response.status_code}")
        elif(400 <= response.status_code < 500):
            logger.error(f"{response.status_code} thrown by API.")
            raise OpenFoodFactsError(f"{response.status_code}")

        data = response.json()
        return data


    def _fetch_page(self, page: int):
        retryer = Retrying(
            stop=stop_after_attempt(self.settings.max_retry_attempts),
            wait=wait_exponential(
                multiplier=self.settings.backoff_multiplier,
                min=self.settings.backoff_min_seconds,
                max=self.settings.backoff_max_seconds,
            ),
            retry=retry_if_exception_type(TransientAPIError),
            reraise=True,
        )
        return retryer(self._fetch_page_once, page)
    

    def iter_products(self, since_epoch: int | None = None) -> Iterator[dict]:
        page = 1
        is_done = False
        while page <= self.settings.max_page_per_run and not is_done :
            data = self._fetch_page(page)
            products = data['products']

            if products == []:
                is_done = True
                break

            for product in products:

                last_modified = product.get('last_modified_t')

                if since_epoch is not None and last_modified < since_epoch:
                    is_done = True
                    break
                yield product
            page+=1
    
