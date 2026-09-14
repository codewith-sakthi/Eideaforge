"""
competition_routes.py – Competition CRUD, round & criteria management, and registration.
"""
from flask import Blueprint, request, g
from middleware.role_middleware import admin_required, student_required
from middleware.auth_middleware import jwt_required
from services import competition_service
from models import competition_model, evaluator_model
from utils.response_utils import success, error, not_found

competition_bp = Blueprint("competitions", __name__)


@competition_bp.route("", methods=["GET"])
def list_competitions():
    status = request.args.get("status")
    comps = competition_model.get_all(status)
    return success(data=comps)


@competition_bp.route("/<int:comp_id>", methods=["GET"])
def get_competition(comp_id: int):
    comp = competition_service.get_competition_details(comp_id)
    if not comp:
        return not_found("Competition not found")
    return success(data=comp)


@competition_bp.route("", methods=["POST"])
@admin_required
def create_competition():
    data = request.get_json() or {}
    result = competition_service.create_competition(g.current_user["id"], data)
    if not result.get("success"):
        return error(result.get("error", "Creation failed"), status=400)
    return success(data={"id": result["id"]}, message="Competition created successfully", status=201)


@competition_bp.route("/<int:comp_id>", methods=["PUT"])
@admin_required
def update_competition(comp_id: int):
    data = request.get_json() or {}
    result = competition_service.update_competition(comp_id, data)
    if not result.get("success"):
        return error(result.get("error", "Update failed"), status=400)
    return success(message="Competition updated successfully")


@competition_bp.route("/<int:comp_id>/register", methods=["POST"])
@student_required
def register_team(comp_id: int):
    data = request.get_json() or {}
    team_id = data.get("team_id")
    if not team_id:
        return error("team_id is required", status=400)

    result = competition_service.register_team(comp_id, team_id, g.current_user["id"])
    if not result.get("success"):
        return error(result.get("error", "Registration failed"), status=400)
    return success(message="Team registered for competition successfully")


@competition_bp.route("/<int:comp_id>/evaluators", methods=["GET"])
@admin_required
def get_assigned_evaluators(comp_id: int):
    evaluators = competition_model.get_assigned_evaluators(comp_id)
    return success(data=evaluators)


@competition_bp.route("/<int:comp_id>/evaluators", methods=["POST"])
@admin_required
def assign_evaluator(comp_id: int):
    data = request.get_json() or {}
    evaluator_id = data.get("evaluator_id")
    round_id = data.get("round_id")
    if not evaluator_id:
        return error("evaluator_id is required", status=400)

    evaluator_model.assign_to_competition(evaluator_id, comp_id, round_id)
    return success(message="Evaluator assigned successfully")


@competition_bp.route("/<int:comp_id>/evaluators/<int:eval_id>", methods=["DELETE"])
@admin_required
def remove_evaluator(comp_id: int, eval_id: int):
    round_id = request.args.get("round_id")
    evaluator_model.remove_assignment(eval_id, comp_id, round_id)
    return success(message="Evaluator assignment removed")


@competition_bp.route("/rounds/<int:round_id>/criteria", methods=["GET"])
def get_round_criteria(round_id: int):
    criteria = competition_model.get_criteria(round_id)
    return success(data=criteria)


@competition_bp.route("/rounds/<int:round_id>/criteria", methods=["POST"])
@admin_required
def add_round_criterion(round_id: int):
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    max_score = data.get("max_score", 10)
    weightage = data.get("weightage", 1.0)
    desc = data.get("description", "")

    if not name:
        return error("Criterion name is required", status=400)

    cid = competition_model.add_criterion(round_id, name, max_score, weightage, desc)
    return success(data={"id": cid}, message="Criterion added successfully", status=201)
