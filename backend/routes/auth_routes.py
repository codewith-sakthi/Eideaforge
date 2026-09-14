"""
auth_routes.py – Authentication and account management endpoints.
"""
from flask import Blueprint, request, g
from services import auth_service
from middleware.auth_middleware import jwt_required
from utils.response_utils import success, error, unauthorized

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    result = auth_service.login(email, password)
    if not result.get("success"):
        return error(result.get("error", "Login failed"), status=401)
    return success(data=result, message="Login successful")


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    data = request.get_json() or {}
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")

    result = auth_service.change_password(g.current_user["id"], old_pw, new_pw)
    if not result.get("success"):
        return error(result.get("error", "Failed to change password"), status=400)
    return success(message="Password changed successfully")


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    return success(data=g.current_user, message="Profile fetched")
