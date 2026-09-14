"""
user_model.py – Core user account operations.
"""
from models import query_one, query_all, execute


def find_by_email(email: str) -> dict | None:
    return query_one("SELECT * FROM users WHERE email = %s", (email,))


def find_by_id(user_id: int) -> dict | None:
    return query_one("SELECT id, email, role, is_active, force_password_change FROM users WHERE id = %s", (user_id,))


def create_user(email: str, password_hash: str, role: str, force_change: bool = True) -> int:
    return execute(
        "INSERT INTO users (email, password_hash, role, is_active, force_password_change) VALUES (%s,%s,%s,1,%s)",
        (email, password_hash, role, 1 if force_change else 0),
    )


def update_password(user_id: int, new_hash: str) -> None:
    execute(
        "UPDATE users SET password_hash=%s, force_password_change=0 WHERE id=%s",
        (new_hash, user_id),
    )


def set_active(user_id: int, is_active: bool) -> None:
    execute("UPDATE users SET is_active=%s WHERE id=%s", (1 if is_active else 0, user_id))


def get_all_by_role(role: str) -> list[dict]:
    return query_all(
        "SELECT id, email, role, is_active, force_password_change, created_at FROM users WHERE role=%s ORDER BY id DESC",
        (role,),
    )
