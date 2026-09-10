from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.models.schemas import UserCreate, UserResponse, UserUpdate, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles, get_password_hash
from app.services.notification_service import log_audit_event
from app.routes.users_data import mock_users_db

router = APIRouter(prefix="/users", tags=["Users"])

def auto_assign_mentor(department_id: str) -> Optional[str]:
    """Finds mentor in department with lowest mentee count and returns mentor_id."""
    department_mentors = [
        u for u in mock_users_db.values()
        if u["role"] == UserRole.MENTOR and u.get("department_id") == department_id
    ]
    if not department_mentors:
        return None

    # Count mentees per mentor
    mentor_counts = {m["id"]: 0 for m in department_mentors}
    for u in mock_users_db.values():
        if u["role"] == UserRole.STUDENT and u.get("mentor_id") in mentor_counts:
            mentor_counts[u["mentor_id"]] += 1

    # Return mentor with minimum assigned count (Round-Robin logic)
    sorted_mentors = sorted(mentor_counts.items(), key=lambda x: x[1])
    return sorted_mentors[0][0]

@router.get("", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = None,
    department_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    users = list(mock_users_db.values())

    # Strict Scope Enforcement
    if current_user.role == UserRole.HOD:
        # HOD is strictly scoped to their own department
        users = [u for u in users if u.get("department_id") == current_user.department_id]
    elif current_user.role == UserRole.MENTOR:
        # Mentor is strictly scoped to their assigned mentees
        users = [u for u in users if u.get("mentor_id") == current_user.user_id or u["id"] == current_user.user_id]
    elif current_user.role == UserRole.STUDENT:
        # Student can only view self
        users = [u for u in users if u["id"] == current_user.user_id]

    if role:
        users = [u for u in users if u["role"] == role]
    if department_id and current_user.role == UserRole.ADMIN:
        users = [u for u in users if u.get("department_id") == department_id]

    return users

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD]))
):
    email = user_data.email.lower()
    if email in mock_users_db:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # HOD can only create users in their department
    if current_user.role == UserRole.HOD:
        user_data.department_id = current_user.department_id

    # Auto round-robin mentor assignment for new students if mentor not specified
    if user_data.role == UserRole.STUDENT and not user_data.mentor_id and user_data.department_id:
        user_data.mentor_id = auto_assign_mentor(user_data.department_id)

    new_id = f"usr_{len(mock_users_db) + 101}"
    user_entry = {
        "id": new_id,
        "name": user_data.name,
        "email": email,
        "phone": user_data.phone,
        "role": user_data.role,
        "department_id": user_data.department_id,
        "mentor_id": user_data.mentor_id,
        "profile_photo": user_data.profile_photo or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.name}",
        "password_hash": get_password_hash(user_data.password)
    }

    mock_users_db[email] = user_entry

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="CREATE_USER",
        target=new_id,
        details=f"Created {user_data.role} user '{user_data.name}' with email '{email}'"
    )

    return user_entry

@router.put("/{user_id}/reassign-mentor")
async def reassign_mentor(
    user_id: str,
    mentor_id: str,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD]))
):
    student = next((u for u in mock_users_db.values() if u["id"] == user_id), None)
    if not student or student["role"] != UserRole.STUDENT:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == UserRole.HOD and student.get("department_id") != current_user.department_id:
        raise HTTPException(status_code=403, detail="Cannot reassign student outside your department")

    mentor = next((u for u in mock_users_db.values() if u["id"] == mentor_id), None)
    if not mentor or mentor["role"] != UserRole.MENTOR:
        raise HTTPException(status_code=400, detail="Invalid mentor ID")

    student["mentor_id"] = mentor_id

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="REASSIGN_MENTOR",
        target=user_id,
        details=f"Reassigned student {student['name']} to mentor {mentor['name']}"
    )

    return {"status": "success", "message": f"Student assigned to mentor {mentor['name']}"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))
):
    target_email = next((e for e, u in mock_users_db.items() if u["id"] == user_id), None)
    if not target_email:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_user = mock_users_db.pop(target_email)

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="DELETE_USER",
        target=user_id,
        details=f"Deleted user {deleted_user['name']} ({deleted_user['email']})"
    )

    return {"status": "success", "message": "User deleted successfully"}
