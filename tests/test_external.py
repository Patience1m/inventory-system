from unittest.mock import Mock, patch
import pytest
import requests
from app.openfoodfacts import ExternalAPIError, fetch_by_barcode, search_by_name

def fake_response(payload):
    mock = Mock()
    mock.json.return_value = payload
    mock.raise_for_status.return_value = None
    return mock

@patch("app.openfoodfacts.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_get.return_value = fake_response(
        {"status": 1, "product": {"product_name": "Almond Milk", "brands": "Silk",
                                  "ingredients_text": "Water, almonds"}})
    result = fetch_by_barcode("123")
    assert result == {"barcode": "123", "product_name": "Almond Milk",
                      "brands": "Silk", "ingredients_text": "Water, almonds"}
    assert "123" in mock_get.call_args[0][0]

@patch("app.openfoodfacts.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = fake_response({"status": 0})
    assert fetch_by_barcode("000") is None

@patch("app.openfoodfacts.requests.get")
def test_fetch_missing_fields_get_defaults(mock_get):
    mock_get.return_value = fake_response({"status": 1, "product": {}})
    result = fetch_by_barcode("1")
    assert result["product_name"] == "Unknown" and result["brands"] == ""

@patch("app.openfoodfacts.requests.get", side_effect = requests.ConnectionError("no net"))
def test_fetch_network_error(mock_get):
    with pytest.raises(ExternalAPIError):
        fetch_by_barcode("123")

@patch("app.openfoodfacts.requests.get")
def test_fetch_http_error(mock_get):
    response = fake_response({})
    response.raise_for_status.side_effect = requests.HTTPError("500")
    mock_get.return_value = response
    with pytest.raises(ExternalAPIError):
        fetch_by_barcode("123")

@patch("app.openfoodfacts.requests.get")
def test_search_by_name(mock_get):
    mock_get.return_value = fake_response(
        {"hits": [{"code": "1", "product_name": "A", "brands": "B"},
                  {"code": "2", "product_name": "C"}]})
    results = search_by_name("milk")
    assert [product["barcode"] for product in results] == ["1", "2"]
    assert mock_get.call_args.kwargs["params"]["q"] == "milk"

@patch("app.openfoodfacts.requests.get", side_effect = requests.Timeout("slow"))
def test_search_timeout(mock_get):
    with pytest.raises(ExternalAPIError):
        search_by_name("milk")