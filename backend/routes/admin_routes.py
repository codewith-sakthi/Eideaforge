"""
admin_routes.py – Administrator dashboard, student management, bulk upload, and platform supervision.
"""
from flask import Blueprint, request, g, send_file
import os
from middleware.role_middleware import admin_required
from models import student_model, evaluator_model, idea_model, competition_model, submission_model, user_model
from services import bulk_upload_service
from utils.response_utils import success, error, not_found

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    students = student_model.get_all()
    evaluators = evaluator_model.get_all()
    ideas = idea_model.get_all()
    competitions = competition_model.get_all()
    submissions = submission_model.get_all()

    return success(data={
        "students_count": len(students),
        "evaluators_count": len(evaluators),
        "ideas_count": len(ideas),
        "competitions_count": len(competitions),
        "submissions_count": len(submissions),
        "recent_ideas": ideas[:5],
        "recent_competitions": competitions[:5],
        "recent_submissions": submissions[:5]
    })


@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    students = student_model.get_all()
    return success(data=students)


@admin_bp.route("/students/<int:student_id>", methods=["GET"])
@admin_required
def get_student(student_id: int):
    student = student_model.get_profile(student_id)
    if not student:
        return not_found("Student not found")
    return success(data=student)


@admin_bp.route("/students/bulk-upload", methods=["POST"])
@admin_required
def bulk_upload():
    if "file" not in request.files:
        return error("No CSV file uploaded", status=400)
    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return error("Only CSV files are allowed", status=400)

    result = bulk_upload_service.process_student_csv(file)
    if not result.get("success", True):
        return error(result.get("error", "Failed to process CSV file"), status=400)
    return success(data=result, message=f"Processed: {result['created']} created, {result['skipped']} skipped.")


@admin_bp.route("/bulk-upload/history", methods=["GET"])
@admin_required
def bulk_upload_history():
    history = bulk_upload_service.get_upload_history()
    return success(data=history)


@admin_bp.route("/bulk-upload/download/<filename>", methods=["GET"])
@admin_required
def download_credentials_file(filename: str):
    fpath = bulk_upload_service.get_credentials_file_path(filename)
    if not fpath:
        return not_found("Credentials file not found")
    return send_file(
        fpath,
        mimetype="text/csv",
        as_attachment=True,
        download_name=os.path.basename(fpath)
    )



@admin_bp.route("/evaluators", methods=["GET"])
@admin_required
def get_evaluators():
    evaluators = evaluator_model.get_all()
    return success(data=evaluators)


@admin_bp.route("/evaluators", methods=["POST"])
@admin_required
def create_evaluator():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    full_name = data.get("full_name", "").strip()
    department = data.get("department", "").strip()
    designation = data.get("designation", "").strip()

    if not email or not full_name:
        return error("Email and Full Name are required", status=400)

    from utils.password_utils import generate_temp_password, hash_password
    temp_pw = generate_temp_password()
    hashed = hash_password(temp_pw)

    user_id = user_model.create_user(email, hashed, "evaluator")
    if not user_id:
        return error("User with this email already exists", status=400)

    evaluator_model.upsert_profile(user_id, {
        "full_name": full_name,
        "department": department,
        "designation": designation
    })

    return success(data={"user_id": user_id, "temp_password": temp_pw}, message="Evaluator created successfully")
