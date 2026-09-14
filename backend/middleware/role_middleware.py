"""
role_middleware.py – Role-based access control decorators.
"""
from functools import wraps
from flask import g
from utils.response_utils import forbidden
from middleware.auth_middleware import jwt_required


def _role_required(*roles):
    """Internal factory: creates a decorator that checks for allowed roles."""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated(*args, **kwargs):
            if g.current_user.get("role") not in roles:
                return forbidden(
                    f"This action requires one of: {', '.join(roles)}."
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    """Allow only admin users."""
    return _role_required("admin")(f)


def student_required(f):
    """Allow only student users."""
    return _role_required("student")(f)


def evaluator_required(f):
    """Allow only evaluator users."""
    return _role_required("evaluator")(f)


def admin_or_evaluator_required(f):
    """Allow admin or evaluator."""
    return _role_required("admin", "evaluator")(f)
