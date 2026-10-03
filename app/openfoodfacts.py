import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryLab/1.0 (student@example.com)"}
SEARCH_URL = "https://search.openfoodfacts.org/search"

class ExternalAPIError(Exception):
    pass

def normalize(product, barcode = None):
    return {
        "barcode": barcode or product.get("code", ""),
        "product_name": product.get("product_name") or "Unknown",
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
    }

def fetch_by_barcode(barcode):
    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/product/{barcode}.json",
            headers = HEADERS,
            timeout = 10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as error:
        raise ExternalAPIError(str(error)) from error
    if data.get("status") != 1:
        return None
    return normalize(data["product"], barcode)

def search_by_name(name, limit = 5):
    try:
        response = requests.get(
            SEARCH_URL,
            headers = HEADERS,
            timeout = 10,
            params = {"q": name, "page_size": limit, "fields": "code,product_name,brands"})
        response.raise_for_status()
        products = response.json().get("hits", [])
    except (requests.RequestException, ValueError) as error:
        raise ExternalAPIError(str(error)) from error
    return [normalize(product) for product in products]