"""
team_service.py – Business logic for team management.
"""
from models import team_model


def create_team(leader_id: int, data: dict) -> dict:
    name = (data.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "Team name is required."}
    
    idea_id = data.get("idea_id")
    if idea_id:
        try:
            idea_id = int(idea_id)
        except (ValueError, TypeError):
            idea_id = None
            
    team_id = team_model.create(
        leader_id=leader_id,
        name=name,
        idea_id=idea_id,
    )
    return {"success": True, "team_id": team_id}


def update_team(team_id: int, leader_id: int, data: dict) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] != leader_id:
        return {"success": False, "error": "Only the team leader can update team details.", "status": 403}
    
    name = (data.get("name") or team["name"]).strip()
    if not name:
        return {"success": False, "error": "Team name cannot be empty."}
    
    idea_id = data.get("idea_id")
    if idea_id is not None:
        try:
            idea_id = int(idea_id) if idea_id else None
        except (ValueError, TypeError):
            idea_id = None
    else:
        idea_id = team["idea_id"]
        
    team_model.update(team_id, name, idea_id)
    return {"success": True, "message": "Team updated successfully."}


def delete_team(team_id: int, leader_id: int) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] != leader_id:
        return {"success": False, "error": "Only the team leader can delete or disband the team.", "status": 403}
    
    team_model.delete(team_id)
    return {"success": True, "message": "Team disbanded successfully."}


def add_member_by_identifier(team_id: int, leader_id: int, identifier: str, role: str = "Member") -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] != leader_id:
        return {"success": False, "error": "Only the team leader can add members directly.", "status": 403}
    
    student = team_model.find_student_by_identifier(identifier)
    if not student:
        return {"success": False, "error": f"No student found matching '{identifier}'. Please verify their Roll Number or Email."}
    
    student_id = student["id"]
    if team_model.is_member(team_id, student_id):
        return {"success": False, "error": f"{student['full_name'] or student['email']} is already in this team."}
    
    role = (role or "Member").strip()
    team_model.add_member(team_id, student_id, role)
    return {
        "success": True,
        "message": f"Added {student['full_name'] or student['email']} to the team.",
        "student": student,
    }


def remove_member(team_id: int, requester_id: int, target_student_id: int) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    
    is_leader = (team["leader_id"] == requester_id)
    is_self = (requester_id == target_student_id)
    
    if not is_leader and not is_self:
        return {"success": False, "error": "You do not have permission to remove this member.", "status": 403}
    
    if is_self and is_leader:
        # Leader trying to remove themselves
        members = team_model.get_members(team_id)
        if len(members) > 1:
            return {"success": False, "error": "As the leader, you must transfer leadership to another member before leaving, or disband the team."}
        else:
            # Only leader left, deleting member will effectively orphan or disband
            team_model.delete(team_id)
            return {"success": True, "message": "Team disbanded as the last member left."}
            
    team_model.remove_member(team_id, target_student_id)
    msg = "You have left the team." if is_self else "Member removed from team."
    return {"success": True, "message": msg}


def update_member_role(team_id: int, leader_id: int, target_student_id: int, role: str) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] != leader_id:
        return {"success": False, "error": "Only the team leader can change member roles.", "status": 403}
    
    role = (role or "Member").strip()
    if not role:
        return {"success": False, "error": "Role name cannot be empty."}
        
    team_model.update_member_role(team_id, target_student_id, role)
    return {"success": True, "message": "Member role updated."}


def transfer_leadership(team_id: int, current_leader_id: int, new_leader_id: int) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] != current_leader_id:
        return {"success": False, "error": "Only current team leader can transfer leadership.", "status": 403}
    if current_leader_id == new_leader_id:
        return {"success": False, "error": "You are already the team leader."}
    if not team_model.is_member(team_id, new_leader_id):
        return {"success": False, "error": "New leader must be an existing member of the team."}
        
    team_model.transfer_leadership(team_id, new_leader_id)
    # Demote old leader to 'Member' / 'Core Member'
    team_model.update_member_role(team_id, current_leader_id, "Co-Founder / Core Member")
    return {"success": True, "message": "Leadership transferred successfully."}


def send_join_request(team_id: int, student_id: int, message: str | None = None) -> dict:
    team = team_model.get_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found.", "status": 404}
    if team["leader_id"] == student_id:
        return {"success": False, "error": "You cannot request to join your own team."}
    if team_model.is_member(team_id, student_id):
        return {"success": False, "error": "You are already a member of this team."}
    
    team_model.send_join_request(team_id, student_id, message)
    return {"success": True}


def respond_join_request(req_id: int, leader_id: int, action: str) -> dict:
    req = team_model.get_join_request_by_id(req_id)
    if not req:
        return {"success": False, "error": "Join request not found.", "status": 404}
    if req["leader_id"] != leader_id:
        return {"success": False, "error": "Only the team leader can respond to join requests.", "status": 403}
    if action not in ("approved", "rejected", "accept", "reject"):
        return {"success": False, "error": "Action must be 'approved' or 'rejected'."}
    
    team_model.respond_join_request(req_id, action)
    return {"success": True, "action": action}

handle_join_request = respond_join_request

