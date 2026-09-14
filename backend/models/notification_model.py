"""
notification_model.py – In-app notification operations.
(Phase 1: stored in DB, displayed on dashboard — email is future phase.)
"""
from models import query_all, execute


def create(user_id: int, message: str, link: str | None = None) -> int:
    return execute(
        "INSERT INTO notifications (user_id, message, link) VALUES (%s,%s,%s)",
        (user_id, message, link),
    )


def get_unread(user_id: int) -> list[dict]:
    return query_all(
        "SELECT * FROM notifications WHERE user_id=%s AND is_read=0 ORDER BY created_at DESC LIMIT 20",
        (user_id,),
    )


def mark_read(user_id: int) -> None:
    execute("UPDATE notifications SET is_read=1 WHERE user_id=%s", (user_id,))


def mark_one_read(notif_id: int) -> None:
    execute("UPDATE notifications SET is_read=1 WHERE id=%s", (notif_id,))
