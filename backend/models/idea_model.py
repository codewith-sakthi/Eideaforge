"""
idea_model.py – Idea CRUD operations with prototype & abstract attachments.
"""
from models import query_one, query_all, execute


def ensure_idea_schema():
    """Ensure abstract_doc_url, github_url, and drive_url columns exist in ideas table."""
    try:
        cols = [r["Field"] for r in query_all("SHOW COLUMNS FROM ideas")]
        if "abstract_doc_url" not in cols:
            execute("ALTER TABLE ideas ADD COLUMN abstract_doc_url VARCHAR(255) NULL AFTER tags")
        if "github_url" not in cols:
            execute("ALTER TABLE ideas ADD COLUMN github_url VARCHAR(255) NULL AFTER abstract_doc_url")
        if "drive_url" not in cols:
            execute("ALTER TABLE ideas ADD COLUMN drive_url VARCHAR(255) NULL AFTER github_url")
    except Exception as e:
        print(f"[Schema Notice] ideas table check: {e}")


# Run schema check at module load / startup
try:
    ensure_idea_schema()
except Exception:
    pass


def get_by_id(idea_id: int) -> dict | None:
    idea = query_one(
        """SELECT i.*, sp.full_name as author_name, u.email as author_email
           FROM ideas i
           JOIN users u ON u.id = i.student_id
           LEFT JOIN student_profiles sp ON sp.user_id = i.student_id
           WHERE i.id = %s""",
        (idea_id,),
    )
    if not idea:
        return None

    # Check for linked team and its members
    team = query_one(
        """SELECT t.*, sp.full_name as leader_name
           FROM teams t
           LEFT JOIN student_profiles sp ON sp.user_id = t.leader_id
           WHERE t.idea_id = %s LIMIT 1""",
        (idea_id,),
    )
    if team:
        members = query_all(
            """SELECT tm.*, sp.full_name, sp.roll_number, sp.department, u.email
               FROM team_members tm
               JOIN users u ON u.id = tm.student_id
               LEFT JOIN student_profiles sp ON sp.user_id = tm.student_id
               WHERE tm.team_id = %s""",
            (team["id"],),
        )
        team["members"] = members
        comp_reg = query_one(
            """SELECT cr.*, c.title as comp_title, c.id as comp_id, c.status as comp_status
               FROM competition_registrations cr
               JOIN competitions c ON c.id = cr.competition_id
               WHERE cr.team_id = %s LIMIT 1""",
            (team["id"],),
        )
        team["competition"] = comp_reg
        idea["team"] = team
    else:
        idea["team"] = None

    return idea


def get_by_user(user_id: int) -> list[dict]:
    return query_all(
        """SELECT i.*, sp.full_name as author_name
           FROM ideas i
           LEFT JOIN student_profiles sp ON sp.user_id = i.student_id
           WHERE i.student_id = %s
           ORDER BY i.updated_at DESC""",
        (user_id,),
    )


def get_all(status: str | None = None) -> list[dict]:
    if status:
        return query_all(
            """SELECT i.*, sp.full_name as author_name, u.email
               FROM ideas i JOIN users u ON u.id=i.student_id
               LEFT JOIN student_profiles sp ON sp.user_id=i.student_id
               WHERE i.status=%s ORDER BY i.updated_at DESC""",
            (status,),
        )
    return query_all(
        """SELECT i.*, sp.full_name as author_name, u.email
           FROM ideas i JOIN users u ON u.id=i.student_id
           LEFT JOIN student_profiles sp ON sp.user_id=i.student_id
           ORDER BY i.updated_at DESC"""
    )


def create(
    student_id: int,
    title: str,
    description: str = "",
    problem_statement: str = "",
    solution: str = "",
    category: str = "",
    tags: str = "",
    status: str = "draft",
    abstract_doc_url: str | None = None,
    github_url: str | None = None,
    drive_url: str | None = None
) -> int:
    ensure_idea_schema()
    return execute(
        """INSERT INTO ideas (student_id, title, description, problem_statement, solution, category, tags, status, abstract_doc_url, github_url, drive_url)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (student_id, title, description, problem_statement, solution, category, tags, status, abstract_doc_url, github_url, drive_url),
    )


def update(idea_id: int, data: dict) -> None:
    ensure_idea_schema()
    execute(
        """UPDATE ideas
           SET title=%s, description=%s, problem_statement=%s, solution=%s, category=%s, tags=%s,
               status=%s, abstract_doc_url=%s, github_url=%s, drive_url=%s, updated_at=NOW()
           WHERE id=%s""",
        (
            data.get("title"), data.get("description"), data.get("problem_statement"),
            data.get("solution"), data.get("category"), data.get("tags"),
            data.get("status", "draft"), data.get("abstract_doc_url"),
            data.get("github_url"), data.get("drive_url"),
            idea_id,
        ),
    )


def update_status(idea_id: int, status: str, admin_notes: str | None = None) -> None:
    execute(
        "UPDATE ideas SET status=%s, updated_at=NOW() WHERE id=%s",
        (status, idea_id),
    )

