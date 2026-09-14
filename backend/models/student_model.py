"""
student_model.py – Student profile operations.
"""
from models import query_one, query_all, execute


def _ensure_schema():
    try:
        execute("ALTER TABLE student_profiles ADD COLUMN domain VARCHAR(150) NULL AFTER skills")
    except Exception:
        pass


def get_profile(user_id: int) -> dict | None:
    _ensure_schema()
    return query_one(
        """SELECT sp.*, u.email, u.is_active, u.force_password_change
           FROM student_profiles sp
           JOIN users u ON u.id = sp.user_id
           WHERE sp.user_id = %s""",
        (user_id,),
    )


def upsert_profile(user_id: int, data: dict) -> None:
    _ensure_schema()
    execute(
        """INSERT INTO student_profiles
               (user_id, full_name, roll_number, department, year_of_study, bio, skills, domain, linkedin_url, github_url)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE
               full_name=%s, department=%s, year_of_study=%s, bio=%s, skills=%s, domain=%s, linkedin_url=%s, github_url=%s""",
        (
            user_id,
            data.get("full_name"), data.get("roll_number"),
            data.get("department"), data.get("year_of_study"),
            data.get("bio"), data.get("skills"), data.get("domain"),
            data.get("linkedin_url"), data.get("github_url"),
            data.get("full_name"), data.get("department"),
            data.get("year_of_study"), data.get("bio"), data.get("skills"),
            data.get("domain"), data.get("linkedin_url"), data.get("github_url"),
        ),
    )


def get_all_students() -> list[dict]:
    _ensure_schema()
    return query_all(
        """SELECT u.id, u.email, u.is_active, sp.full_name, sp.roll_number,
                  sp.department, sp.year_of_study, sp.bio, sp.skills, sp.domain
           FROM users u
           LEFT JOIN student_profiles sp ON sp.user_id = u.id
           WHERE u.role = 'student'
           ORDER BY u.id DESC"""
    )


get_all = get_all_students


def get_student_detail(user_id: int) -> dict | None:
    _ensure_schema()
    return query_one(
        """SELECT u.id, u.email, u.is_active, sp.full_name, sp.roll_number,
                  sp.department, sp.year_of_study, sp.bio, sp.skills, sp.domain,
                  sp.linkedin_url, sp.github_url
           FROM users u
           LEFT JOIN student_profiles sp ON sp.user_id = u.id
           WHERE u.id = %s AND u.role = 'student'""",
        (user_id,),
    )

