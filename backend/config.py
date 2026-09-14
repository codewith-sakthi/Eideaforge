"""
config.py – Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

# Load .env from backend directory as well as current working directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
load_dotenv()



class Config:
    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "0") == "1"
    PORT: int = int(os.environ.get("PORT", 5000))

    # ── JWT ────────────────────────────────────────────────────────────────
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "dev-jwt-secret-change-me")
    JWT_EXPIRY_HOURS: int = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

    # ── Database ───────────────────────────────────────────────────────────
    MYSQL_HOST: str = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB: str = os.environ.get("MYSQL_DB", "eideaforge")

    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), "uploads", "pitches")
    CREDENTIALS_FOLDER: str = os.path.join(os.path.dirname(__file__), "uploads", "credentials")
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 16)) * 1024 * 1024
    ALLOWED_PITCH_EXTENSIONS: set = {"pdf", "ppt", "pptx"}

    # ── CORS ───────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list = [
        o.strip()
        for o in os.environ.get(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500"
        ).split(",")
        if o.strip()
    ]
