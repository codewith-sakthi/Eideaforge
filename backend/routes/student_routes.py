"""
student_routes.py – Student dashboard, profile, and student-specific views.
"""
from flask import Blueprint, request, g
from middleware.role_middleware import student_required
from models import student_model, idea_model, team_model, competition_model, submission_model, notification_model
from utils.response_utils import success, error

student_bp = Blueprint("student", __name__)


@student_bp.route("/dashboard", methods=["GET"])
@student_required
def dashboard():
    user_id = g.current_user["id"]
    profile = student_model.get_profile(user_id)
    ideas = idea_model.get_by_user(user_id)
    teams = team_model.get_by_user(user_id)
    submissions = submission_model.get_by_user(user_id)
    notifications = notification_model.get_unread(user_id)

    return success(data={
        "profile": profile,
        "ideas_count": len(ideas),
        "teams_count": len(teams),
        "submissions_count": len(submissions),
        "recent_ideas": ideas[:5],
        "teams": teams,
        "submissions": submissions[:5],
        "notifications": notifications
    })


@student_bp.route("/profile", methods=["GET"])
@student_required
def get_profile():
    user_id = g.current_user["id"]
    profile = student_model.get_profile(user_id)
    return success(data=profile)


@student_bp.route("/profile", methods=["PUT"])
@student_required
def update_profile():
    user_id = g.current_user["id"]
    data = request.get_json() or {}
    
    full_name = (data.get("full_name") or "").strip()
    skills = (data.get("skills") or "").strip()
    domain = (data.get("domain") or "").strip()

    if not full_name:
        return error("Full Name is mandatory", status=400)
    if not skills:
        return error("Technical & Design Skills are mandatory. Please enter your skills.", status=400)
    if not domain:
        return error("Focus Domain / Area of Expertise is mandatory. Please specify your domain.", status=400)

    student_model.upsert_profile(user_id, data)
    return success(message="Profile updated successfully")



@student_bp.route("/submissions", methods=["GET"])
@student_required
def get_my_submissions():
    user_id = g.current_user["id"]
    submissions = submission_model.get_by_user(user_id)
    return success(data=submissions)
