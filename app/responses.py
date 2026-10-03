from flask import jsonify

def api_response(data = None, message = "OK", success = True, status_code = 200):
    payload = {
        "success" : success,
        "message" : message,
        "data" : data if data is not None else "",
    }
    return jsonify(payload), status_code

def validation_error(message = "Validation failed"):
    return api_response(
        message = message,
        success = False,
        status_code = 422
    )

def not_found(message = "Resource not found"):
    return api_response(
        message = message,
        success = False,
        status_code = 404
    )