"""
idea_routes.py – Idea creation, listing, updating, and admin review endpoints.
"""
from flask import Blueprint, request, g
from middleware.auth_middleware import jwt_required
from middleware.role_middleware import admin_required, student_required
from services import idea_service
from models import idea_model
from utils.response_utils import success, error, not_found, forbidden

idea_bp = Blueprint("ideas", __name__)


@idea_bp.route("", methods=["GET"])
@jwt_required
def list_ideas():
    status = request.args.get("status")
    user_role = g.current_user["role"]

    if user_role == "admin":
        ideas = idea_service.get_all_ideas(status)
    elif user_role == "student":
        # Check if requesting user's own ideas or public ideas
        scope = request.args.get("scope")
        if scope == "mine":
            ideas = idea_service.get_user_ideas(g.current_user["id"])
        else:
            ideas = idea_service.get_all_ideas("approved")
    else:
        ideas = idea_service.get_all_ideas("approved")

    return success(data=ideas)


@idea_bp.route("/<int:idea_id>", methods=["GET"])
@jwt_required
def get_idea(idea_id: int):
    idea = idea_model.get_by_id(idea_id)
    if not idea:
        return not_found("Idea not found")
    
    # Students can view if it's their own or if approved
    if g.current_user["role"] == "student":
        if idea["student_id"] != g.current_user["id"] and idea["status"] != "approved":
            return forbidden("Access denied to draft or under review idea")
            
    return success(data=idea)


@idea_bp.route("/upload-abstract", methods=["POST"])
@student_required
def upload_abstract():
    from middleware.upload_middleware import save_abstract_file
    if "file" not in request.files:
        return error("No file uploaded under 'file' key", status=400)
    
    file = request.files["file"]
    rel_path, err = save_abstract_file(file)
    if err:
        return err
    return success(data={"file_url": f"/{rel_path}".replace("\\", "/")}, message="Abstract document uploaded successfully")


@idea_bp.route("", methods=["POST"])
@student_required
def create_idea():
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()
        if "file" in request.files and request.files["file"].filename:
            from middleware.upload_middleware import save_abstract_file
            rel_path, err = save_abstract_file(request.files["file"])
            if not err:
                data["abstract_doc_url"] = f"/{rel_path}".replace("\\", "/")

    result = idea_service.create_idea(g.current_user["id"], data)
    if not result.get("success"):
        return error(result.get("error", "Failed to create idea"), status=400)
    return success(data={"id": result["idea_id"]}, message="Idea created successfully", status=201)


@idea_bp.route("/<int:idea_id>", methods=["PUT"])
@student_required
def update_idea(idea_id: int):
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()
        if "file" in request.files and request.files["file"].filename:
            from middleware.upload_middleware import save_abstract_file
            rel_path, err = save_abstract_file(request.files["file"])
            if not err:
                data["abstract_doc_url"] = f"/{rel_path}".replace("\\", "/")

    result = idea_service.update_idea(idea_id, g.current_user["id"], data)
    if not result.get("success"):
        return error(result.get("error", "Update failed"), status=result.get("status", 400))
    return success(message="Idea updated successfully")


@idea_bp.route("/<int:idea_id>/status", methods=["PATCH"])
@admin_required
def update_idea_status(idea_id: int):
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ["draft", "submitted", "approved", "rejected"]:
        return error("Invalid status", status=400)

    result = idea_service.admin_review(idea_id, new_status)
    if not result.get("success"):
        return error(result.get("error", "Review failed"), status=400)
    return success(message=f"Idea status updated to {new_status}")

