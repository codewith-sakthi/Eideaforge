"""
auth_service.py – Login, registration, and password change business logic.
"""
from models.user_model import find_by_email, update_password
from utils.password_utils import verify_password, hash_password, generate_temp_password
from utils.jwt_utils import generate_token
from utils.validators import validate_password_strength


def login(email: str, password: str) -> dict:
    """
    Authenticate a user. Returns a dict with keys:
      success, token, user, force_password_change, error
    """
    user = find_by_email(email)
    if not user:
        return {"success": False, "error": "Invalid email or password."}
    if not user["is_active"]:
        return {"success": False, "error": "Your account has been deactivated. Contact admin."}
    if not verify_password(password, user["password_hash"]):
        return {"success": False, "error": "Invalid email or password."}

    token = generate_token(user["id"], user["role"], user["email"])
    full_name = None
    if user["role"] == "student":
        from models.student_model import get_profile
        sp = get_profile(user["id"])
        if sp:
            full_name = sp.get("full_name")
    elif user["role"] == "evaluator":
        from models.evaluator_model import get_profile
        ep = get_profile(user["id"])
        if ep:
            full_name = ep.get("full_name")

    return {
        "success": True,
        "token": token,
        "user": {
            "id":    user["id"],
            "email": user["email"],
            "role":  user["role"],
            "full_name": full_name,
            "force_password_change": bool(user["force_password_change"]),
        },
    }


def change_password(user_id: int, current_password: str, new_password: str) -> dict:
    from models.user_model import find_by_id
    from models import query_one
    user = query_one("SELECT * FROM users WHERE id=%s", (user_id,))
    if not user:
        return {"success": False, "error": "User not found."}
    if not verify_password(current_password, user["password_hash"]):
        return {"success": False, "error": "Current password is incorrect."}
    valid, msg = validate_password_strength(new_password)
    if not valid:
        return {"success": False, "error": msg}
    if verify_password(new_password, user["password_hash"]):
        return {"success": False, "error": "New password must differ from current password."}
    update_password(user_id, hash_password(new_password))
    return {"success": True}
