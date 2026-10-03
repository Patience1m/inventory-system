from flask import Blueprint, request
from app.data import add_item, find_item, inventory
from app.models import InventoryItem
from app.responses import api_response, not_found, validation_error

inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix = "/inventory")

@inventory_bp.route("", methods=["GET"])
def list_all_items():
    return api_response(
        message = "Inventory retrieved",
        data = inventory
    )

@inventory_bp.route("", methods=["POST"])
def create_item():
    try:
        item = InventoryItem(**(request.get_json(silent = True) or {}))
    except (ValueError, TypeError) as error:
        return validation_error(str(error))
    return api_response(
        message = "Item successfully created",
        status_code = 201,
        data = add_item(item)
    )

@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found("Item not found")
    return api_response(data = item)

@inventory_bp.route("/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found("Item not found")
    payload = request.get_json(silent = True) or {}
    try:
        updated_item = InventoryItem(**{**item, **payload})
    except (ValueError, TypeError) as error:
        return validation_error(str(error))
    if updated_item.id != item["id"]:
        return validation_error("id cannot be changed")
    item.update(updated_item.to_dict())
    return api_response(
        message = "Item successfully updated",
        data = item
    )

@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return not_found("Item not found")
    inventory.remove(item)
    return "", 204