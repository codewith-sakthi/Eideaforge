"""
idea_service.py – Business logic for idea operations.
"""
from models import idea_model


def get_user_ideas(user_id: int) -> list:
    return idea_model.get_by_user(user_id)


def get_all_ideas(status: str | None = None) -> list:
    return idea_model.get_all(status)


def create_idea(user_id: int, data: dict, submit: bool = False) -> dict:
    # Enforce only one idea per student
    existing_ideas = idea_model.get_by_user(user_id)
    if existing_ideas:
        return {
            "success": False,
            "error": "You already have an innovation pitch registered. Each student can manage 1 idea. Please edit your existing idea.",
            "existing_idea_id": existing_ideas[0]["id"],
        }

    title = (data.get("title") or "").strip()
    if not title:
        return {"success": False, "error": "Title is required."}
    
    status = "submitted" if (submit or data.get("status") == "submitted") else "draft"
    
    idea_id = idea_model.create(
        student_id=user_id,
        title=title,
        description=(data.get("description") or "").strip(),
        problem_statement=(data.get("problem_statement") or "").strip(),
        solution=(data.get("solution") or "").strip(),
        category=(data.get("category") or "").strip(),
        tags=(data.get("tags") or "").strip(),
        status=status,
        abstract_doc_url=data.get("abstract_doc_url"),
        github_url=(data.get("github_url") or "").strip() or None,
        drive_url=(data.get("drive_url") or "").strip() or None,
    )
    return {"success": True, "idea_id": idea_id, "status": status}



def update_idea(idea_id: int, user_id: int, data: dict) -> dict:
    idea = idea_model.get_by_id(idea_id)
    if not idea:
        return {"success": False, "error": "Idea not found.", "status": 404}
    if idea.get("student_id") != user_id:
        return {"success": False, "error": "Permission denied.", "status": 403}
    if idea.get("status") not in ("draft", "submitted", "rejected"):
        return {"success": False, "error": "Only draft, submitted or rejected ideas can be edited."}
    
    # Merge existing URLs if not provided
    if "abstract_doc_url" not in data and "abstract_doc_url" in idea:
        data["abstract_doc_url"] = idea.get("abstract_doc_url")
    if "github_url" not in data and "github_url" in idea:
        data["github_url"] = idea.get("github_url")
    if "drive_url" not in data and "drive_url" in idea:
        data["drive_url"] = idea.get("drive_url")
        
    idea_model.update(idea_id, data)
    return {"success": True}



def admin_review(idea_id: int, status: str, admin_notes: str | None = None) -> dict:
    idea = idea_model.get_by_id(idea_id)
    if not idea:
        return {"success": False, "error": "Idea not found.", "status": 404}
    if status not in ("approved", "rejected"):
        return {"success": False, "error": "Status must be 'approved' or 'rejected'."}
    idea_model.update_status(idea_id, status, admin_notes)
    return {"success": True}
