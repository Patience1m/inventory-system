from flask import Blueprint, request
from app import openfoodfacts
from app.data import add_item, inventory
from app.models import InventoryItem
from app.responses import api_response, bad_gateway, not_found, validation_error

lookup_bp = Blueprint("lookup", __name__)

@lookup_bp.route("/lookup/barcode/<code>", methods=["GET"])
def lookup_barcode(code):
    try:
        product = openfoodfacts.fetch_by_barcode(code)
    except openfoodfacts.ExternalAPIError as error:
        return bad_gateway(f"External API failure: {error}")
    if product is None:
        return not_found("Product not found on OpenFoodFacts")
    return api_response(data = product)

@lookup_bp.route("/lookup/search", methods=["GET"])
def lookup_search():
    name = request.args.get("name", "").strip()
    if not name:
        return validation_error("name query parameter is required")
    try:
        results = openfoodfacts.search_by_name(name)
    except openfoodfacts.ExternalAPIError as error:
        return bad_gateway(f"External API failure: {error}")
    return api_response(data = results)


@lookup_bp.route("/inventory/import/<code>", methods=["POST"])
def import_item(code):
    if any(item["barcode"] == code for item in inventory):
        return api_response(
            message = "Barcode already in inventory",
            success = False,
            status_code = 409
        )
    try:
        product = openfoodfacts.fetch_by_barcode(code)
    except openfoodfacts.ExternalAPIError as error:
        return bad_gateway(f"External API failure: {error}")
    if product is None:
        return not_found("Product not found on OpenFoodFacts")
    payload = request.get_json(silent = True) or {}
    try:
        item = InventoryItem(**{**product, **payload})
    except (ValueError, TypeError) as error:
        return validation_error(str(error))
    return api_response(
        message = "Item successfully imported",
        status_code = 201,
        data = add_item(item)
    )