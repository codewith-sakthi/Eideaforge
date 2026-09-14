"""
validators.py – Input validation helpers.
"""
import re


EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
URL_RE   = re.compile(
    r"^https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}"
    r"\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)$"
)


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def validate_url(url: str) -> bool:
    return bool(URL_RE.match(url or ""))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    Rules: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_file_extension(filename: str, allowed: set) -> bool:
    """Check that the file has an allowed extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in allowed


def require_fields(data: dict, fields: list) -> list[str]:
    """Return a list of missing required field names."""
    return [f for f in fields if not data.get(f)]
