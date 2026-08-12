import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type




url = "https://world.openfoodfacts.org/cgi/search.pl"
params = {
    "search_terms": "snacks",
    "search_simple": 1,
    "action": "process",
    "json": 1,
    "page_size": 3,
    "sort_by": "last_modified_t",
}
headers = {
    "User-Agent": "DataEngPortfolioProject/1.0 (contact: lemuelhmgs@yahoo.com)"
}


class UpstreamUnavailable(Exception):
    pass

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(UpstreamUnavailable),
    reraise=True,
)


def fetch_products():
    params = {
        "search_terms": "snacks",
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 3,
        "sort_by": "last_modified_t",
    }
    response = requests.get(url, params=params, headers=headers, timeout=10)

    if response.status_code == 503:
        print(f"Got 503, retrying...")
        raise UpstreamUnavailable("503 Service Unavailable")

    response.raise_for_status()
    return response.json()


data = fetch_products()

print("Total count:", data.get("count"))
print()

for product in data["products"]:
    print("code:", product.get("code"))
    print("product_name:", product.get("product_name"))
    print("last_modified_t:", product.get("last_modified_t"))
    print("categories:", product.get("categories"))
    print("---")