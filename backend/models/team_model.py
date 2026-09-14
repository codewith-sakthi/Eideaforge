"""
team_model.py – Team and join-request operations.
"""
from models import query_one, query_all, execute


def get_by_id(team_id: int) -> dict | None:
    return query_one(
        """SELECT t.*, i.title as idea_title, sp.full_name as leader_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
           FROM teams t
           LEFT JOIN ideas i ON i.id = t.idea_id
           LEFT JOIN student_profiles sp ON sp.user_id = t.leader_id
           WHERE t.id = %s""",
        (team_id,),
    )


def get_by_user(user_id: int) -> list[dict]:
    """Teams where the user is a member."""
    return query_all(
        """SELECT t.*, i.title as idea_title, sp.full_name as leader_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
           FROM teams t
           JOIN team_members tm ON tm.team_id = t.id AND tm.student_id = %s
           LEFT JOIN ideas i ON i.id = t.idea_id
           LEFT JOIN student_profiles sp ON sp.user_id = t.leader_id
           ORDER BY t.created_at DESC""",
        (user_id,),
    )

get_teams_for_user = get_by_user


def get_all() -> list[dict]:
    """All teams with member counts and leader info."""
    return query_all(
        """SELECT t.*, i.title as idea_title, sp.full_name as leader_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
           FROM teams t
           LEFT JOIN ideas i ON i.id = t.idea_id
           LEFT JOIN student_profiles sp ON sp.user_id = t.leader_id
           ORDER BY t.created_at DESC"""
    )


def get_open_teams(exclude_user_id: int) -> list[dict]:
    return query_all(
        """SELECT t.*, i.title as idea_title, sp.full_name as leader_name,
                  (SELECT COUNT(*) FROM team_members WHERE team_id = t.id) as member_count
           FROM teams t
           LEFT JOIN ideas i ON i.id = t.idea_id
           LEFT JOIN student_profiles sp ON sp.user_id = t.leader_id
           WHERE t.leader_id != %s
           ORDER BY t.created_at DESC""",
        (exclude_user_id,),
    )


def create(leader_id: int, name: str, idea_id: int | None = None) -> int:
    team_id = execute(
        "INSERT INTO teams (name, leader_id, idea_id) VALUES (%s, %s, %s)",
        (name, leader_id, idea_id if idea_id else None),
    )
    # Auto-add leader as Member with 'Leader' role
    execute(
        "INSERT IGNORE INTO team_members (team_id, student_id, role) VALUES (%s, %s, 'Leader')",
        (team_id, leader_id),
    )
    return team_id


def get_members(team_id: int) -> list[dict]:
    return query_all(
        """SELECT tm.*, sp.full_name, sp.roll_number, sp.department, u.email
           FROM team_members tm
           JOIN users u ON u.id = tm.student_id
           LEFT JOIN student_profiles sp ON sp.user_id = tm.student_id
           WHERE tm.team_id = %s
           ORDER BY tm.joined_at ASC""",
        (team_id,),
    )


def is_member(team_id: int, student_id: int) -> bool:
    row = query_one(
        "SELECT 1 FROM team_members WHERE team_id = %s AND student_id = %s",
        (team_id, student_id),
    )
    return bool(row)


def send_join_request(team_id: int, student_id: int, message: str | None = None) -> int:
    return execute(
        "INSERT INTO join_requests (team_id, student_id, message, status) VALUES (%s, %s, %s, 'pending')",
        (team_id, student_id, message or ""),
    )


def get_received_requests(leader_id: int) -> list[dict]:
    return query_all(
        """SELECT jr.*, t.name as team_name, sp.full_name as student_name, sp.roll_number, sp.department, u.email as student_email
           FROM join_requests jr
           JOIN teams t ON t.id = jr.team_id AND t.leader_id = %s
           JOIN users u ON u.id = jr.student_id
           LEFT JOIN student_profiles sp ON sp.user_id = jr.student_id
           WHERE jr.status = 'pending'
           ORDER BY jr.created_at DESC""",
        (leader_id,),
    )

get_incoming_requests = get_received_requests


def get_sent_requests(student_id: int) -> list[dict]:
    return query_all(
        """SELECT jr.*, t.name as team_name
           FROM join_requests jr
           JOIN teams t ON t.id = jr.team_id
           WHERE jr.student_id = %s
           ORDER BY jr.created_at DESC""",
        (student_id,),
    )

get_outgoing_requests = get_sent_requests


def get_join_request_by_id(req_id: int) -> dict | None:
    return query_one(
        """SELECT jr.*, t.leader_id, t.name as team_name
           FROM join_requests jr
           JOIN teams t ON t.id = jr.team_id
           WHERE jr.id = %s""",
        (req_id,),
    )


def update(team_id: int, name: str, idea_id: int | None = None) -> None:
    execute(
        "UPDATE teams SET name = %s, idea_id = %s WHERE id = %s",
        (name, idea_id if idea_id else None, team_id),
    )


def delete(team_id: int) -> None:
    execute("DELETE FROM teams WHERE id = %s", (team_id,))


def add_member(team_id: int, student_id: int, role: str = 'Member') -> None:
    execute(
        "INSERT INTO team_members (team_id, student_id, role) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE role = VALUES(role)",
        (team_id, student_id, role or 'Member'),
    )


def remove_member(team_id: int, student_id: int) -> None:
    execute(
        "DELETE FROM team_members WHERE team_id = %s AND student_id = %s",
        (team_id, student_id),
    )


def update_member_role(team_id: int, student_id: int, role: str) -> None:
    execute(
        "UPDATE team_members SET role = %s WHERE team_id = %s AND student_id = %s",
        (role, team_id, student_id),
    )


def transfer_leadership(team_id: int, new_leader_id: int) -> None:
    # 1. Update team leader_id
    execute("UPDATE teams SET leader_id = %s WHERE id = %s", (new_leader_id, team_id))
    # 2. Ensure new leader is in team_members as Leader
    execute(
        "INSERT INTO team_members (team_id, student_id, role) VALUES (%s, %s, 'Leader') "
        "ON DUPLICATE KEY UPDATE role = 'Leader'",
        (team_id, new_leader_id),
    )


def get_team_pending_requests(team_id: int) -> list[dict]:
    return query_all(
        """SELECT jr.*, sp.full_name as student_name, sp.roll_number, sp.department, u.email as student_email
           FROM join_requests jr
           JOIN users u ON u.id = jr.student_id
           LEFT JOIN student_profiles sp ON sp.user_id = jr.student_id
           WHERE jr.team_id = %s AND jr.status = 'pending'
           ORDER BY jr.created_at DESC""",
        (team_id,),
    )


def search_available_students(query: str, team_id: int | None = None) -> list[dict]:
    like_q = f"%{query.strip()}%"
    if team_id:
        return query_all(
            """SELECT u.id, u.email, sp.full_name, sp.roll_number, sp.department, sp.year_of_study
               FROM users u
               LEFT JOIN student_profiles sp ON sp.user_id = u.id
               WHERE u.role = 'student' AND u.is_active = 1
                 AND u.id NOT IN (SELECT student_id FROM team_members WHERE team_id = %s)
                 AND (sp.full_name LIKE %s OR sp.roll_number LIKE %s OR u.email LIKE %s)
               ORDER BY sp.full_name ASC
               LIMIT 15""",
            (team_id, like_q, like_q, like_q),
        )
    return query_all(
        """SELECT u.id, u.email, sp.full_name, sp.roll_number, sp.department, sp.year_of_study
           FROM users u
           LEFT JOIN student_profiles sp ON sp.user_id = u.id
           WHERE u.role = 'student' AND u.is_active = 1
             AND (sp.full_name LIKE %s OR sp.roll_number LIKE %s OR u.email LIKE %s)
           ORDER BY sp.full_name ASC
           LIMIT 15""",
        (like_q, like_q, like_q),
    )


def find_student_by_identifier(identifier: str) -> dict | None:
    ident = str(identifier).strip()
    is_num = ident.isdigit()
    return query_one(
        """SELECT u.id, u.email, sp.full_name, sp.roll_number, sp.department
           FROM users u
           LEFT JOIN student_profiles sp ON sp.user_id = u.id
           WHERE u.role = 'student' AND u.is_active = 1
             AND (u.email = %s OR sp.roll_number = %s OR u.id = %s)
           LIMIT 1""",
        (ident, ident, int(ident) if is_num else -1),
    )


def respond_join_request(req_id: int, action: str) -> dict | None:
    req = query_one("SELECT * FROM join_requests WHERE id = %s", (req_id,))
    if not req:
        return None
    
    status = 'approved' if action in ('approved', 'accept', 'accepted') else 'rejected'
    execute("UPDATE join_requests SET status = %s WHERE id = %s", (status, req_id))
    
    if status == 'approved':
        execute(
            "INSERT IGNORE INTO team_members (team_id, student_id, role) VALUES (%s, %s, 'Member')",
            (req["team_id"], req["student_id"]),
        )
    return req

handle_join_request = respond_join_request


