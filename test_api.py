import requests


url = "https://world.openfoodfacts.org/cgi/search.pl"

headers = {
    "User-Agent": "DataEngPortfolioProject/1.0 (contact: your_email@example.com)"
}

params = {
    "search_terms": "cereal",
    "search_simple": 1,
    "action": "process",
    "json": 1,
    "page_size": 5,
}

response = requests.get(url,params=params, headers=headers)

print("Status code: ", response.status_code)

data = response.json()
print("Number of products found:", data.get("count"))
print("First product name:", data["products"][0].get("product_name"))
