"""
upload_middleware.py – File upload validation and saving helpers.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from utils.validators import validate_file_extension
from utils.response_utils import error


ALLOWED_PITCH_EXTENSIONS = {"pdf", "ppt", "pptx"}
ALLOWED_ABSTRACT_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "txt"}


def save_abstract_file(file_storage) -> tuple[str | None, tuple | None]:
    """
    Validate and save an uploaded idea abstract document.
    """
    if not file_storage or file_storage.filename == "":
        return None, error("No file selected.", 400)

    filename = secure_filename(file_storage.filename)
    if not validate_file_extension(filename, ALLOWED_ABSTRACT_EXTENSIONS):
        return None, error(
            "Invalid file type. Only PDF, DOC, DOCX, PPT, PPTX, TXT are allowed.", 400
        )

    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"abstract_{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", "abstracts")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)
    file_storage.save(save_path)

    return os.path.join("uploads", "abstracts", unique_name), None


def save_pitch_file(file_storage) -> tuple[str | None, tuple | None]:
    """
    Validate and save an uploaded pitch deck file.

    Returns:
        (relative_path, None)  on success
        (None, error_response) on failure
    """
    if not file_storage or file_storage.filename == "":
        return None, error("No file selected.", 400)

    filename = secure_filename(file_storage.filename)
    if not validate_file_extension(filename, ALLOWED_PITCH_EXTENSIONS):
        return None, error(
            "Invalid file type. Only PDF, PPT, PPTX are allowed.", 400
        )

    # Unique filename to avoid collisions
    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config.get("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "..", "uploads", "pitches"))
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)
    file_storage.save(save_path)

    # Return a relative path (for DB storage)
    return os.path.join("uploads", "pitches", unique_name), None


def save_pitch_deck(file_storage) -> dict:
    """Convenience dict-returning wrapper for pitch deck saving."""
    rel_path, err = save_pitch_file(file_storage)
    if err:
        return {"success": False, "error": "Invalid file or upload failed"}
    return {"success": True, "relative_path": rel_path}


def allowed_pitch(filename: str) -> bool:
    return validate_file_extension(filename, ALLOWED_PITCH_EXTENSIONS)


