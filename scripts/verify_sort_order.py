"""
Determine whether sort_by=last_modified_t on
/api/v2/search returns newest-first or oldest-first.

Why this matters: our incremental "stop paging once we hit the
watermark" this only works if results are newest-first. If they're
oldest-first, we need a different strategy (e.g. always paging fully,
or finding another filter approach).
"""
import requests

url = "https://world.openfoodfacts.org/api/v2/search"
headers = {
    "User-Agent": "DataEngPortfolioProject/1.0 (contact: lemuelhmgs@yahoo.com)"
}
params = {
    "categories_tags": "snacks",
    "sort_by": "last_modified_t",
    "page": 1,
    "page_size": 1,
    "fields": "code,product_name,last_modified_t",
}

response = requests.get(url, params=params, headers=headers, timeout=15)
response.raise_for_status()
data = response.json()

print(len(data["products"]))

timestamps = [p["last_modified_t"] for p in data["products"]]
print("count (total matching):", data.get("count"))
print("timestamps on page 1, in order returned:")
for t in timestamps:
    print(" ", t)

if timestamps == sorted(timestamps, reverse=True):
    print("\n=> DESCENDING (newest first). Early-stop pagination will work.")
elif timestamps == sorted(timestamps):
    print("\n=> ASCENDING (oldest first). Need a different incremental strategy.")
else:
    print("\n=> Not strictly sorted within this page — inspect manually.")