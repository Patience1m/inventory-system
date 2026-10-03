from unittest.mock import patch
from app import create_app
from app.openfoodfacts import ExternalAPIError

app = create_app("testing")

PRODUCT = {"barcode": "999", "product_name": "Test Bar", "brands": "TestCo",
           "ingredients_text": "Oats"}

@patch("app.openfoodfacts.fetch_by_barcode", return_value = PRODUCT)
def test_lookup_barcode(mock_fetch):
    client = app.test_client()
    response = client.get("/lookup/barcode/999")
    assert response.status_code == 200
    assert response.get_json()["data"]["product_name"] == "Test Bar"

@patch("app.openfoodfacts.fetch_by_barcode", return_value = None)
def test_lookup_barcode_not_found(mock_fetch):
    client = app.test_client()
    response = client.get("/lookup/barcode/000")
    assert response.status_code == 404

@patch("app.openfoodfacts.fetch_by_barcode", side_effect = ExternalAPIError("down"))
def test_lookup_barcode_api_down(mock_fetch):
    client = app.test_client()
    response = client.get("/lookup/barcode/1")
    assert response.status_code == 502

@patch("app.openfoodfacts.search_by_name", return_value = [PRODUCT])
def test_lookup_search(mock_search):
    client = app.test_client()
    response = client.get("/lookup/search?name=bar")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 1

def test_lookup_search_requires_name():
    client = app.test_client()
    response = client.get("/lookup/search")
    assert response.status_code == 422

@patch("app.openfoodfacts.fetch_by_barcode", return_value = PRODUCT)
def test_import_adds_to_inventory(mock_fetch):
    client = app.test_client()
    response = client.post("/inventory/import/999", json={"price": 2.5, "stock": 10})
    assert response.status_code == 201
    assert response.get_json()["data"]["price"] == 2.5
    assert len(client.get("/inventory").get_json()["data"]) == 4

@patch("app.openfoodfacts.fetch_by_barcode", return_value = PRODUCT)
def test_import_duplicate_barcode(mock_fetch):
    client = app.test_client()
    response = client.post("/inventory/import/3017620422003")
    assert response.status_code == 409

@patch("app.openfoodfacts.fetch_by_barcode", return_value = None)
def test_import_unknown_barcode(mock_fetch):
    client = app.test_client()
    response = client.post("/inventory/import/000")
    assert response.status_code == 404