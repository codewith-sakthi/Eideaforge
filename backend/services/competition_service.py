"""
competition_service.py – Competition business logic.
"""
from models import competition_model


def get_public_competitions() -> dict:
    return {
        "ongoing":   competition_model.get_all("ongoing"),
        "upcoming":  competition_model.get_all("upcoming"),
        "completed": competition_model.get_all("completed"),
    }


def get_competition_detail(comp_id: int) -> dict | None:
    comp = competition_model.get_by_id(comp_id)
    if not comp:
        return None
    return {
        **comp,
        "rounds":   competition_model.get_rounds(comp_id),
        "criteria": competition_model.get_criteria(comp_id),
    }

get_competition_details = get_competition_detail



def create_competition(admin_id: int, data: dict) -> dict:
    if not data.get("title"):
        return {"success": False, "error": "Title is required."}
    comp_id = competition_model.create(admin_id, data)
    return {"success": True, "comp_id": comp_id}


def update_competition(comp_id: int, data: dict) -> dict:
    if not competition_model.get_by_id(comp_id):
        return {"success": False, "error": "Competition not found.", "status": 404}
    competition_model.update(comp_id, data)
    return {"success": True}


def register_team(comp_id: int, team_id: int, user_id: int = None) -> dict:
    from models.competition_model import get_registered_teams, register_team as db_register_team
    from models.team_model import get_by_id
    team = get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found."}
    if user_id and team.get("leader_id") != user_id:
        return {"success": False, "error": "Only the team leader can register the team for competitions."}
    already = [t for t in get_registered_teams(comp_id) if t.get("team_id") == team_id]
    if already:
        return {"success": False, "error": "This team is already registered for this competition."}
    db_register_team(comp_id, team_id)
    return {"success": True}
