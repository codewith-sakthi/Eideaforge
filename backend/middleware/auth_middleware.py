"""
auth_middleware.py – JWT authentication decorator for protected routes.
"""
from functools import wraps
from flask import request, g
import jwt as pyjwt

from utils.jwt_utils import extract_token, decode_token
from utils.response_utils import unauthorized


def jwt_required(f):
    """
    Decorator: validates JWT in Authorization header.
    Sets g.current_user = { id, role, email } on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token(request.headers.get("Authorization", ""))
        if not token:
            return unauthorized("No token provided. Please log in.")
        try:
            payload = decode_token(token)
            g.current_user = {
                "id":    payload["sub"],
                "role":  payload["role"],
                "email": payload["email"],
            }
        except pyjwt.ExpiredSignatureError:
            return unauthorized("Token has expired. Please log in again.")
        except pyjwt.InvalidTokenError:
            return unauthorized("Invalid token. Please log in again.")
        return f(*args, **kwargs)
    return decorated
