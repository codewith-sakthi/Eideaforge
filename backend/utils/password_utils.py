"""
password_utils.py – Password hashing and verification using Werkzeug.
"""
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string


def hash_password(plain: str) -> str:
    """Return a bcrypt-style hash of the plain-text password."""
    return generate_password_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    return check_password_hash(hashed, plain)


def generate_temp_password(length: int = 12) -> str:
    """Generate a cryptographically secure temporary password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        # Ensure at least one of each required character type
        if (
            any(c.islower() for c in pwd)
            and any(c.isupper() for c in pwd)
            and any(c.isdigit() for c in pwd)
        ):
            return pwd
