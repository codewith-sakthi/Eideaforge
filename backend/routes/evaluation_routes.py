"""
evaluation_routes.py – Rubric scoring, leaderboard, and competition results.
"""
from flask import Blueprint, request, g
from middleware.role_middleware import evaluator_required, admin_required
from middleware.auth_middleware import jwt_required
from services import evaluation_service
from models import evaluation_model
from utils.response_utils import success, error, not_found

evaluation_bp = Blueprint("evaluations", __name__)


@evaluation_bp.route("/submissions/<int:sub_id>/score", methods=["POST"])
@evaluator_required
def score_submission(sub_id: int):
    """
    Body payload:
    {
      "scores": {
        "<criterion_id>": { "score": 8.5, "comments": "Strong technical foundation" },
        ...
      }
    }
    """
    data = request.get_json() or {}
    scores = data.get("scores", {})
    if not scores:
        return error("Scores payload is empty", status=400)

    result = evaluation_service.submit_scores(sub_id, g.current_user["id"], scores)
    if not result.get("success"):
        return error(result.get("error", "Failed to submit scores"), status=400)
    return success(message="Scores saved successfully")


@evaluation_bp.route("/competitions/<int:comp_id>/leaderboard", methods=["GET"])
@jwt_required
def get_leaderboard(comp_id: int):
    round_id = request.args.get("round_id")
    rid = int(round_id) if round_id else None
    leaderboard = evaluation_service.get_leaderboard(comp_id, rid)
    return success(data=leaderboard)


@evaluation_bp.route("/competitions/<int:comp_id>/results", methods=["GET"])
@jwt_required
def get_student_results(comp_id: int):
    user_id = g.current_user["id"]
    results = evaluation_service.get_student_result(comp_id, user_id)
    return success(data=results)
