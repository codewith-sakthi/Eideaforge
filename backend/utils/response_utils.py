"""
response_utils.py – Standardised JSON response helpers.

All API responses follow the shape:
  { "success": bool, "data": any, "message": str, "error": str }
"""
from flask import jsonify


def success(data=None, message: str = "OK", status: int = 200):
    return jsonify({"success": True, "data": data, "message": message}), status


def created(data=None, message: str = "Created"):
    return success(data, message, 201)


def error(message: str = "An error occurred", status: int = 400, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


def not_found(resource: str = "Resource"):
    return error(f"{resource} not found", 404)


def forbidden(message: str = "Access denied"):
    return error(message, 403)


def unauthorized(message: str = "Authentication required"):
    return error(message, 401)


def server_error(message: str = "Internal server error"):
    return error(message, 500)
