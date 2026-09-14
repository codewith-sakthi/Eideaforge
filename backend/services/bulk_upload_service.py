"""
bulk_upload_service.py – CSV import for students and credential generation.
"""
import csv
import io
import os
from models.user_model import create_user, find_by_email
from models.student_model import upsert_profile
from utils.password_utils import generate_temp_password, hash_password
from config import Config

REQUIRED_COLUMNS = {"full_name", "roll_number", "email"}


def process_student_csv(file_or_content) -> dict:
    """
    Parse a CSV file and bulk-create student accounts.

    Returns:
      { created: int, skipped: int, errors: [...], credentials: [...] }
    """
    if hasattr(file_or_content, "read"):
        raw = file_or_content.read()
        if isinstance(raw, bytes):
            content = raw.decode("utf-8-sig", errors="ignore")
        else:
            content = str(raw)
    elif isinstance(file_or_content, bytes):
        content = file_or_content.decode("utf-8-sig", errors="ignore")
    else:
        content = str(file_or_content)

    reader = csv.DictReader(io.StringIO(content))

    # Normalise headers
    reader.fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]

    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        return {"success": False, "error": f"Missing columns: {', '.join(missing)}"}

    created, skipped, errors, credentials = 0, 0, [], []

    for i, row in enumerate(reader, start=2):  # row 1 = header
        email = (row.get("email") or "").strip().lower()
        full_name = (row.get("full_name") or "").strip()
        roll_number = (row.get("roll_number") or "").strip()

        if not email or not full_name or not roll_number:
            errors.append(f"Row {i}: Missing required fields.")
            continue

        if find_by_email(email):
            skipped += 1
            continue

        department = (row.get("department") or "").strip() or None
        year_of_study = int(row.get("year_of_study") or 0) or None
        phone = (row.get("phone") or "").strip() or None

        temp_pw = generate_temp_password()
        user_id = create_user(email, hash_password(temp_pw), "student", force_change=True)
        upsert_profile(user_id, {
            "full_name":    full_name,
            "roll_number":  roll_number,
            "department":   department,
            "year_of_study": year_of_study,
            "phone":        phone,
            "bio":          None,
        })
        credentials.append({
            "name": full_name,
            "email": email,
            "temp_password": temp_pw,
            "roll_number": roll_number,
            "department": department or "N/A",
            "year_of_study": str(year_of_study) if year_of_study else "N/A",
        })
        created += 1

    # Write credentials to a CSV in uploads/credentials/
    cred_path = None
    filename = None
    if credentials:
        import uuid, datetime
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"credentials_{timestamp_str}_{uuid.uuid4().hex[:4]}.csv"
        cred_path = os.path.join(Config.CREDENTIALS_FOLDER, filename)
        os.makedirs(Config.CREDENTIALS_FOLDER, exist_ok=True)
        with open(cred_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["name", "email", "temp_password", "roll_number", "department", "year_of_study"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(credentials)

    return {
        "success": True,
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "credentials_file": filename,
        "credentials": credentials,  # returned in response for immediate display & client download
    }


def get_upload_history() -> list[dict]:
    """
    Scans the credentials folder and returns a chronological list of past bulk upload batches.
    """
    folder = Config.CREDENTIALS_FOLDER
    if not os.path.exists(folder):
        return []

    import datetime
    history = []

    for fname in os.listdir(folder):
        if not fname.endswith(".csv"):
            continue

        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue

        stat = os.stat(fpath)
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        size_bytes = stat.st_size
        size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes > 1024 else f"{size_bytes} B"

        # Read CSV rows to get student count and sample preview
        records = []
        try:
            with open(fpath, "r", encoding="utf-8-sig", errors="ignore") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    records.append({
                        "name": r.get("name") or r.get("full_name") or "",
                        "email": r.get("email") or "",
                        "temp_password": r.get("temp_password") or "",
                        "roll_number": r.get("roll_number") or "",
                        "department": r.get("department") or "",
                        "year_of_study": r.get("year_of_study") or "",
                    })
        except Exception:
            records = []

        history.append({
            "filename": fname,
            "uploaded_at": mtime.strftime("%b %d, %Y %I:%M %p"),
            "timestamp": stat.st_mtime,
            "file_size": size_str,
            "student_count": len(records),
            "records": records,
        })

    # Sort descending by timestamp
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    return history


def get_credentials_file_path(filename: str) -> str | None:
    """
    Safely resolve a credentials filename to avoid path traversal.
    """
    clean_name = os.path.basename(filename)
    fpath = os.path.join(Config.CREDENTIALS_FOLDER, clean_name)
    if os.path.exists(fpath) and os.path.isfile(fpath):
        return fpath
    return None

