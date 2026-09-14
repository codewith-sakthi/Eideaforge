"""
public_routes.py – Public landing page, competition catalog, and platform info.
"""
from flask import Blueprint, request
from services import competition_service
from models import competition_model
from utils.response_utils import success, not_found

public_bp = Blueprint("public", __name__)


@public_bp.route("/competitions", methods=["GET"])
def list_competitions():
    status = request.args.get("status")
    if status:
        comps = competition_model.get_all(status)
        return success(data=comps)
    data = competition_service.get_public_competitions()
    return success(data=data)


@public_bp.route("/competitions/<int:comp_id>", methods=["GET"])
def competition_details(comp_id: int):
    comp = competition_service.get_competition_details(comp_id)
    if not comp:
        return not_found("Competition not found")
    return success(data=comp)


@public_bp.route("/stats", methods=["GET"])
def public_stats():
    # Return overview stats for public landing page
    from models import query_one
    stats = {
        "ideas_count": (query_one("SELECT COUNT(*) as c FROM ideas WHERE status='approved'") or {}).get("c", 0),
        "teams_count": (query_one("SELECT COUNT(*) as c FROM teams") or {}).get("c", 0),
        "competitions_count": (query_one("SELECT COUNT(*) as c FROM competitions") or {}).get("c", 0),
        "students_count": (query_one("SELECT COUNT(*) as c FROM users WHERE role='student'") or {}).get("c", 0)
    }
    return success(data=stats)
