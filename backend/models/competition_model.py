"""
competition_model.py – Competition, round, and criteria operations.
"""
from models import query_one, query_all, execute


# ── Competitions ──────────────────────────────────────────────────────────────

def get_all(status: str | None = None) -> list[dict]:
    base = "SELECT * FROM competitions"
    if status:
        return query_all(base + " WHERE status=%s ORDER BY id DESC", (status,))
    return query_all(base + " ORDER BY id DESC")


def get_by_id(comp_id: int) -> dict | None:
    return query_one("SELECT * FROM competitions WHERE id=%s", (comp_id,))


def create(admin_id: int, data: dict) -> int:
    return execute(
        """INSERT INTO competitions
               (title, description, rules, eligibility, status,
                registration_start, registration_end, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            data["title"], data.get("description"), data.get("rules"),
            data.get("eligibility"), data.get("status", "draft"),
            data.get("registration_start"), data.get("registration_end"),
            admin_id,
        ),
    )


def update(comp_id: int, data: dict) -> None:
    execute(
        """UPDATE competitions SET title=%s, description=%s, rules=%s, eligibility=%s,
                status=%s, registration_start=%s, registration_end=%s
           WHERE id=%s""",
        (
            data["title"], data.get("description"), data.get("rules"),
            data.get("eligibility"), data.get("status"),
            data.get("registration_start"), data.get("registration_end"),
            comp_id,
        ),
    )


# ── Rounds ────────────────────────────────────────────────────────────────────

def get_rounds(comp_id: int) -> list[dict]:
    return query_all(
        "SELECT * FROM competition_rounds WHERE competition_id=%s ORDER BY round_number", (comp_id,)
    )


def add_round(comp_id: int, data: dict) -> int:
    next_num = (query_one(
        "SELECT COALESCE(MAX(round_number),0)+1 as n FROM competition_rounds WHERE competition_id=%s",
        (comp_id,),
    ) or {}).get("n", 1)
    return execute(
        """INSERT INTO competition_rounds
               (competition_id, round_number, name, description, submission_start, submission_end)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (comp_id, next_num, data["name"], data.get("description"),
         data.get("submission_start"), data.get("submission_end")),
    )


def activate_round(comp_id: int, round_id: int) -> None:
    execute("UPDATE competition_rounds SET is_current=0 WHERE competition_id=%s", (comp_id,))
    execute("UPDATE competition_rounds SET is_current=1 WHERE id=%s AND competition_id=%s", (round_id, comp_id))


# ── Criteria ──────────────────────────────────────────────────────────────────

def get_criteria(comp_id: int) -> list[dict]:
    return query_all(
        """SELECT ec.*, ec.weightage as weight, cr.title as round_title
           FROM evaluation_criteria ec
           JOIN competition_rounds cr ON cr.id = ec.round_id
           WHERE cr.competition_id = %s
           ORDER BY ec.id""",
        (comp_id,),
    )


def add_criterion(comp_id: int, data: dict) -> int:
    round_id = data.get("round_id")
    if not round_id:
        r = query_one("SELECT id FROM competition_rounds WHERE competition_id=%s ORDER BY round_number ASC LIMIT 1", (comp_id,))
        round_id = r["id"] if r else None
    if not round_id:
        round_id = add_round(comp_id, {"name": "Round 1", "description": "Initial Round"})
    return execute(
        "INSERT INTO evaluation_criteria (round_id, name, description, max_score, weightage) VALUES (%s,%s,%s,%s,%s)",
        (round_id, data["name"], data.get("description"), data.get("max_score", 10), data.get("weight", data.get("weightage", 1.0))),
    )


# ── Registrations ─────────────────────────────────────────────────────────────

def get_registrations_for_user(user_id: int) -> list[dict]:
    """All competitions a student's teams are registered in."""
    return query_all(
        """SELECT cr.*, c.title, c.status, t.name as team_name
           FROM competition_registrations cr
           JOIN competitions c ON c.id=cr.competition_id
           JOIN teams t ON t.id=cr.team_id
           WHERE cr.team_id IN (
               SELECT team_id FROM team_members WHERE student_id=%s
           )""",
        (user_id,),
    )


def register_team(comp_id: int, team_id: int) -> int:
    return execute(
        "INSERT IGNORE INTO competition_registrations (competition_id, team_id) VALUES (%s,%s)",
        (comp_id, team_id),
    )


def get_registered_teams(comp_id: int) -> list[dict]:
    return query_all(
        """SELECT cr.*, t.name as team_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id=t.id) as member_count,
                  sp.full_name as leader_name
           FROM competition_registrations cr
           JOIN teams t ON t.id=cr.team_id
           LEFT JOIN student_profiles sp ON sp.user_id=t.leader_id
           WHERE cr.competition_id=%s""",
        (comp_id,),
    )
