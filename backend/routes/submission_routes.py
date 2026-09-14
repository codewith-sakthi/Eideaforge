"""
submission_routes.py – Submission uploads (pitch deck, git prototype, video demo) and review.
"""
from flask import Blueprint, request, g, current_app
from middleware.role_middleware import student_required, admin_required
from middleware.auth_middleware import jwt_required
from middleware.upload_middleware import save_pitch_deck
from models import submission_model, competition_model, team_model
from utils.response_utils import success, error, not_found, forbidden

submission_bp = Blueprint("submissions", __name__)


@submission_bp.route("", methods=["GET"])
@jwt_required
def list_submissions():
    comp_id = request.args.get("competition_id")
    round_id = request.args.get("round_id")
    status = request.args.get("status")

    if g.current_user["role"] == "admin":
        subs = submission_model.get_all(comp_id, round_id, status)
    elif g.current_user["role"] == "student":
        subs = submission_model.get_by_user(g.current_user["id"])
    else:
        subs = []
    return success(data=subs)


@submission_bp.route("/<int:sub_id>", methods=["GET"])
@jwt_required
def get_submission(sub_id: int):
    sub = submission_model.get_by_id(sub_id)
    if not sub:
        return not_found("Submission not found")
    return success(data=sub)


@submission_bp.route("", methods=["POST"])
@student_required
def submit():
    # Supports multipart/form-data for file upload
    team_id = request.form.get("team_id")
    comp_id = request.form.get("competition_id")
    round_id = request.form.get("round_id")
    prototype_url = request.form.get("prototype_url", "").strip() or None
    demo_video_url = request.form.get("demo_video_url", "").strip() or None
    notes = request.form.get("notes", "").strip() or None

    if not team_id or not comp_id or not round_id:
        return error("team_id, competition_id, and round_id are required", status=400)

    # Validate team leader/member
    team = team_model.get_by_id(int(team_id))
    if not team or team["leader_id"] != g.current_user["id"]:
        return forbidden("Only the team leader can submit entries")

    # Handle pitch deck file
    pitch_deck_file = request.files.get("pitch_deck")
    pitch_path = None
    if pitch_deck_file and pitch_deck_file.filename != "":
        res = save_pitch_deck(pitch_deck_file)
        if not res.get("success"):
            return error(res.get("error"), status=400)
        pitch_path = res.get("relative_path")
    else:
        return error("Pitch deck file (PDF or PPT/PPTX) is required", status=400)

    sub_id = submission_model.create(
        team_id=int(team_id),
        competition_id=int(comp_id),
        round_id=int(round_id),
        pitch_deck_path=pitch_path,
        prototype_url=prototype_url,
        demo_video_url=demo_video_url,
        notes=notes
    )

    return success(data={"id": sub_id}, message="Submission created successfully", status=201)


@submission_bp.route("/<int:sub_id>/status", methods=["PATCH"])
@admin_required
def update_submission_status(sub_id: int):
    data = request.get_json() or {}
    new_status = data.get("status")
    feedback = data.get("feedback")

    if new_status not in ["pending", "approved", "rejected", "evaluated"]:
        return error("Invalid status", status=400)

    submission_model.update_status(sub_id, new_status, feedback)
    return success(message=f"Submission marked as {new_status}")
