"""
submission_model.py – Submission CRUD operations.
"""
from models import query_one, query_all, execute


def get_by_id(sub_id: int) -> dict | None:
    return query_one(
        """SELECT s.*, t.name as team_name, c.title as comp_title, cr.title as round_name
           FROM submissions s
           JOIN teams t ON t.id=s.team_id
           JOIN competitions c ON c.id=s.competition_id
           JOIN competition_rounds cr ON cr.id=s.round_id
           WHERE s.id=%s""",
        (sub_id,),
    )


def get_by_team_round(team_id: int, round_id: int) -> dict | None:
    return query_one(
        "SELECT * FROM submissions WHERE team_id=%s AND round_id=%s", (team_id, round_id)
    )


def get_for_user(user_id: int) -> list[dict]:
    return query_all(
        """SELECT s.*, c.title as comp_title, cr.title as round_name, t.name as team_name
           FROM submissions s
           JOIN competitions c ON c.id=s.competition_id
           JOIN competition_rounds cr ON cr.id=s.round_id
           JOIN teams t ON t.id=s.team_id
           WHERE s.team_id IN (
               SELECT team_id FROM team_members WHERE student_id=%s
           )
           ORDER BY s.submitted_at DESC""",
        (user_id,),
    )


def get_all_submissions(comp_id: int | None = None) -> list[dict]:
    if comp_id:
        return query_all(
            """SELECT s.*, t.name as team_name, c.title as comp_title, cr.title as round_name,
                      sp.full_name as leader_name
               FROM submissions s
               JOIN teams t ON t.id=s.team_id
               JOIN competitions c ON c.id=s.competition_id
               JOIN competition_rounds cr ON cr.id=s.round_id
               LEFT JOIN student_profiles sp ON sp.user_id=t.leader_id
               WHERE s.competition_id=%s ORDER BY s.submitted_at DESC""",
            (comp_id,),
        )
    return query_all(
        """SELECT s.*, t.name as team_name, c.title as comp_title, cr.title as round_name
           FROM submissions s
           JOIN teams t ON t.id=s.team_id
           JOIN competitions c ON c.id=s.competition_id
           JOIN competition_rounds cr ON cr.id=s.round_id
           ORDER BY s.submitted_at DESC"""
    )

get_all = get_all_submissions


def create(data: dict) -> int:
    return execute(
        """INSERT INTO submissions
               (team_id, competition_id, round_id, pitch_file_path,
                github_link, demo_video_link, additional_notes, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,'submitted')""",
        (
            data["team_id"], data["competition_id"], data["round_id"],
            data.get("pitch_file_path"), data.get("github_link"),
            data.get("demo_video_link"), data.get("additional_notes"),
        ),
    )


def update_status(sub_id: int, status: str, feedback: str | None = None) -> None:
    execute(
        "UPDATE submissions SET status=%s, admin_feedback=%s WHERE id=%s",
        (status, feedback, sub_id),
    )


def get_open_rounds_for_user(user_id: int) -> list[dict]:
    """Rounds currently open for submission for the student's teams."""
    return query_all(
        """SELECT cr.*, c.title as comp_title, c.id as competition_id,
                  t.id as team_id, t.name as team_name
           FROM competition_rounds cr
           JOIN competitions c ON c.id=cr.competition_id
           JOIN competition_registrations creg ON creg.competition_id=c.id
           JOIN teams t ON t.id=creg.team_id
           WHERE cr.is_current=1
             AND (cr.submission_end IS NULL OR cr.submission_end > NOW())
             AND t.id IN (SELECT team_id FROM team_members WHERE student_id=%s)
             AND NOT EXISTS (
                 SELECT 1 FROM submissions s WHERE s.round_id=cr.id AND s.team_id=t.id
             )""",
        (user_id,),
    )
