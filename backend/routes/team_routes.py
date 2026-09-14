"""
team_routes.py – Team formation, member management, and join requests.
"""
from flask import Blueprint, request, g
from middleware.role_middleware import student_required
from middleware.auth_middleware import jwt_required
from services import team_service
from models import team_model
from utils.response_utils import success, error, not_found, forbidden

team_bp = Blueprint("teams", __name__)


@team_bp.route("", methods=["GET"])
@jwt_required
def list_teams():
    scope = request.args.get("scope")
    if scope == "mine" and g.current_user["role"] == "student":
        teams = team_model.get_by_user(g.current_user["id"])
    else:
        teams = team_model.get_all()
    return success(data=teams)


@team_bp.route("/search-students", methods=["GET"])
@student_required
def search_students():
    q = request.args.get("q", "")
    team_id = request.args.get("team_id")
    if len(q.strip()) < 1:
        return success(data=[])
    try:
        t_id = int(team_id) if team_id else None
    except ValueError:
        t_id = None
    results = team_model.search_available_students(q, t_id)
    return success(data=results)


@team_bp.route("/<int:team_id>", methods=["GET"])
@jwt_required
def get_team(team_id: int):
    team = team_model.get_by_id(team_id)
    if not team:
        return not_found("Team not found")
    members = team_model.get_members(team_id)
    return success(data={"team": team, "members": members})


@team_bp.route("", methods=["POST"])
@student_required
def create_team():
    data = request.get_json() or {}
    result = team_service.create_team(g.current_user["id"], data)
    if not result.get("success"):
        return error(result.get("error", "Failed to create team"), status=400)
    return success(data={"team_id": result["team_id"]}, message="Team created successfully", status=201)


@team_bp.route("/<int:team_id>", methods=["PUT"])
@student_required
def update_team(team_id: int):
    data = request.get_json() or {}
    result = team_service.update_team(team_id, g.current_user["id"], data)
    if not result.get("success"):
        return error(result.get("error", "Failed to update team"), status=result.get("status", 400))
    return success(message=result.get("message", "Team updated successfully"))


@team_bp.route("/<int:team_id>", methods=["DELETE"])
@student_required
def delete_team(team_id: int):
    result = team_service.delete_team(team_id, g.current_user["id"])
    if not result.get("success"):
        return error(result.get("error", "Failed to delete team"), status=result.get("status", 400))
    return success(message=result.get("message", "Team disbanded successfully"))


@team_bp.route("/<int:team_id>/members", methods=["POST"])
@student_required
def add_member(team_id: int):
    data = request.get_json() or {}
    identifier = str(data.get("identifier") or data.get("student_id") or "").strip()
    role = (data.get("role") or "Member").strip()
    if not identifier:
        return error("Please provide a Student Roll Number, Email, or ID.", status=400)
    
    result = team_service.add_member_by_identifier(team_id, g.current_user["id"], identifier, role)
    if not result.get("success"):
        return error(result.get("error", "Failed to add member"), status=result.get("status", 400))
    return success(message=result.get("message", "Member added successfully"), data=result.get("student"))


@team_bp.route("/<int:team_id>/members/<int:student_id>", methods=["DELETE"])
@student_required
def remove_member(team_id: int, student_id: int):
    result = team_service.remove_member(team_id, g.current_user["id"], student_id)
    if not result.get("success"):
        return error(result.get("error", "Failed to remove member"), status=result.get("status", 400))
    return success(message=result.get("message", "Member removed successfully"))


@team_bp.route("/<int:team_id>/members/<int:student_id>/role", methods=["PUT"])
@student_required
def update_member_role(team_id: int, student_id: int):
    data = request.get_json() or {}
    role = (data.get("role") or "").strip()
    if not role:
        return error("Role cannot be empty", status=400)
    result = team_service.update_member_role(team_id, g.current_user["id"], student_id, role)
    if not result.get("success"):
        return error(result.get("error", "Failed to update role"), status=result.get("status", 400))
    return success(message="Member role updated")


@team_bp.route("/<int:team_id>/transfer-lead", methods=["POST"])
@student_required
def transfer_leadership(team_id: int):
    data = request.get_json() or {}
    new_leader_id = data.get("new_leader_id")
    if not new_leader_id:
        return error("New leader ID is required", status=400)
    try:
        new_leader_id = int(new_leader_id)
    except ValueError:
        return error("Invalid leader ID", status=400)
        
    result = team_service.transfer_leadership(team_id, g.current_user["id"], new_leader_id)
    if not result.get("success"):
        return error(result.get("error", "Failed to transfer leadership"), status=result.get("status", 400))
    return success(message=result.get("message", "Leadership transferred successfully"))


@team_bp.route("/<int:team_id>/join-requests", methods=["GET"])
@student_required
def get_team_join_requests(team_id: int):
    team = team_model.get_by_id(team_id)
    if not team:
        return not_found("Team not found")
    if team["leader_id"] != g.current_user["id"]:
        return forbidden("Only the team leader can view join requests.")
    requests = team_model.get_team_pending_requests(team_id)
    return success(data=requests)


@team_bp.route("/<int:team_id>/join", methods=["POST"])
@student_required
def request_join(team_id: int):
    data = request.get_json() or {}
    message = data.get("message", "")
    result = team_service.send_join_request(team_id, g.current_user["id"], message)
    if not result.get("success"):
        return error(result.get("error", "Request failed"), status=400)
    return success(message="Join request sent")


@team_bp.route("/join-requests", methods=["GET"])
@student_required
def get_join_requests():
    scope = request.args.get("scope", "received")
    if scope == "sent":
        requests = team_model.get_sent_requests(g.current_user["id"])
    else:
        requests = team_model.get_received_requests(g.current_user["id"])
    return success(data=requests)


@team_bp.route("/join-requests/<int:req_id>/action", methods=["POST"])
@student_required
def handle_join_request(req_id: int):
    data = request.get_json() or {}
    action = data.get("action")  # 'approved' or 'rejected'
    if action not in ["approved", "rejected"]:
        return error("Action must be approved or rejected", status=400)

    result = team_service.respond_join_request(req_id, g.current_user["id"], action)
    if not result.get("success"):
        return error(result.get("error", "Action failed"), status=400)
    return success(message=f"Request {action} successfully")

