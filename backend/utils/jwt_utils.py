"""
jwt_utils.py – JWT creation and decoding helpers.
"""
import jwt
import datetime
from config import Config


def generate_token(user_id: int, role: str, email: str) -> str:
    """Generate a signed JWT access token."""
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=Config.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """
    Decode a JWT token. Returns the payload dict.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def extract_token(authorization_header: str) -> str | None:
    """
    Parse the Bearer token from an Authorization header.
    Returns the raw token string or None.
    """
    if not authorization_header:
        return None
    parts = authorization_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
