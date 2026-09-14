"""
evaluator_routes.py – Evaluator dashboard, assigned competitions, and evaluation workflow.
"""
from flask import Blueprint, request, g
from middleware.role_middleware import evaluator_required
from models import evaluator_model, competition_model, submission_model, evaluation_model
from utils.response_utils import success, error, not_found

evaluator_bp = Blueprint("evaluator", __name__)


@evaluator_bp.route("/dashboard", methods=["GET"])
@evaluator_required
def dashboard():
    evaluator_id = g.current_user["id"]
    profile = evaluator_model.get_profile(evaluator_id)
    competitions = evaluator_model.get_assigned_competitions(evaluator_id)
    pending_submissions = evaluation_model.get_submissions_for_evaluator(evaluator_id)
    
    # Filter pending vs evaluated
    pending = [s for s in pending_submissions if not s.get("evaluated")]
    completed = [s for s in pending_submissions if s.get("evaluated")]

    return success(data={
        "profile": profile,
        "assigned_competitions_count": len(competitions),
        "pending_evaluations_count": len(pending),
        "completed_evaluations_count": len(completed),
        "competitions": competitions,
        "pending_submissions": pending[:5],
        "completed_submissions": completed[:5]
    })


@evaluator_bp.route("/competitions", methods=["GET"])
@evaluator_required
def get_competitions():
    evaluator_id = g.current_user["id"]
    comps = evaluator_model.get_assigned_competitions(evaluator_id)
    return success(data=comps)


@evaluator_bp.route("/submissions", methods=["GET"])
@evaluator_required
def get_submissions():
    evaluator_id = g.current_user["id"]
    submissions = evaluation_model.get_submissions_for_evaluator(evaluator_id)
    return success(data=submissions)


@evaluator_bp.route("/submissions/<int:sub_id>", methods=["GET"])
@evaluator_required
def get_submission_detail(sub_id: int):
    evaluator_id = g.current_user["id"]
    sub = submission_model.get_by_id(sub_id)
    if not sub:
        return not_found("Submission not found")
    
    # Get criteria for this round
    criteria = competition_model.get_criteria(sub["round_id"])
    scores = evaluation_model.get_scores_for_submission(sub_id, evaluator_id)
    
    return success(data={
        "submission": sub,
        "criteria": criteria,
        "scores": scores
    })
