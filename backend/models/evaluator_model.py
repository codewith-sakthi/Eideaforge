"""
evaluator_model.py – Evaluator profile and assignment operations.
"""
from models import query_one, query_all, execute


def get_profile(user_id: int) -> dict | None:
    return query_one(
        """SELECT ep.*, u.email, u.is_active
           FROM evaluator_profiles ep
           JOIN users u ON u.id = ep.user_id
           WHERE ep.user_id = %s""",
        (user_id,),
    )


def upsert_profile(user_id: int, data: dict) -> None:
    execute(
        """INSERT INTO evaluator_profiles (user_id, full_name, designation, department, expertise, bio)
           VALUES (%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE full_name=%s, designation=%s, department=%s, expertise=%s, bio=%s""",
        (
            user_id, data.get("full_name"), data.get("designation"),
            data.get("department"), data.get("expertise"), data.get("bio"),
            data.get("full_name"), data.get("designation"),
            data.get("department"), data.get("expertise"), data.get("bio"),
        ),
    )


def get_all_evaluators() -> list[dict]:
    return query_all(
        """SELECT u.id, u.email, u.is_active, ep.full_name, ep.designation, ep.department, ep.expertise, ep.bio
           FROM users u
           LEFT JOIN evaluator_profiles ep ON ep.user_id = u.id
           WHERE u.role = 'evaluator'
           ORDER BY u.id DESC"""
    )

get_all = get_all_evaluators


def get_assignments(evaluator_id: int) -> list[dict]:
    """Return all competitions the evaluator is assigned to."""
    return query_all(
        """SELECT ea.id as assignment_id, ea.round_id, c.id as comp_id, c.title, c.status,
                  cr.title as round_name, cr.round_number
           FROM competition_evaluators ea
           JOIN competitions c ON c.id = ea.competition_id
           LEFT JOIN competition_rounds cr ON cr.id = ea.round_id
           WHERE ea.evaluator_id = %s""",
        (evaluator_id,),
    )

get_assigned_competitions = get_assignments


def assign(evaluator_id: int, comp_id: int, round_id: int | None = None) -> int:
    return execute(
        "INSERT IGNORE INTO competition_evaluators (evaluator_id, competition_id, round_id) VALUES (%s,%s,%s)",
        (evaluator_id, comp_id, round_id),
    )


def remove_assignment(assignment_id: int) -> None:
    execute("DELETE FROM evaluator_assignments WHERE id=%s", (assignment_id,))
