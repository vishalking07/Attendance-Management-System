from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from app.models.schemas import LeaveRequestCreate, ApprovalAction, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles
from app.services.notification_service import create_notification, log_audit_event
from app.routes.users_data import mock_leaves_db, mock_users_db

router = APIRouter(prefix="/leaves", tags=["Leaves"])

@router.get("")
async def list_leaves(
    status_filter: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    leaves = list(mock_leaves_db)

    # Scoping
    if current_user.role == UserRole.STUDENT:
        leaves = [l for l in leaves if l["student_id"] == current_user.user_id]
    elif current_user.role == UserRole.MENTOR:
        mentees = [u["id"] for u in mock_users_db.values() if u.get("mentor_id") == current_user.user_id]
        leaves = [l for l in leaves if l["student_id"] in mentees]
    elif current_user.role == UserRole.HOD:
        leaves = [l for l in leaves if l.get("department_id") == current_user.department_id]

    if status_filter:
        leaves = [l for l in leaves if l["status"] == status_filter]

    return leaves

@router.post("")
async def create_leave_request(
    leave: LeaveRequestCreate,
    current_user: TokenData = Depends(require_roles([UserRole.STUDENT]))
):
    student_id = current_user.user_id
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    
    new_id = f"leave_{len(mock_leaves_db) + 1}"
    entry = {
        "id": new_id,
        "student_id": student_id,
        "student_name": student["name"] if student else "Student",
        "department_id": current_user.department_id,
        "reason": leave.reason,
        "from_date": leave.from_date,
        "to_date": leave.to_date,
        "document_url": leave.document_url,
        "status": "PENDING",  # PENDING, APPROVED, REJECTED, ESCALATED
        "created_at": datetime.utcnow().isoformat(),
        "approval_trail": []
    }
    mock_leaves_db.append(entry)

    if student and student.get("mentor_id"):
        await create_notification(
            user_id=student["mentor_id"],
            title="New Student Leave Request",
            message=f"{student['name']} applied for leave ({leave.from_date} to {leave.to_date}).",
            notification_type="INFO"
        )

    await log_audit_event(
        actor_id=student_id,
        actor_name=student["name"] if student else "Student",
        action="SUBMIT_LEAVE_REQUEST",
        target=new_id,
        details=f"Leave application from {leave.from_date} to {leave.to_date}: {leave.reason}"
    )

    return entry

@router.post("/approve")
async def review_leave_request(
    approval: ApprovalAction,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD, UserRole.MENTOR]))
):
    leave = next((l for l in mock_leaves_db if l["id"] == approval.request_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    action = approval.action.upper()
    leave["status"] = "APPROVED" if action == "APPROVE" else ("REJECTED" if action == "REJECT" else "ESCALATED")

    leave.get("approval_trail", []).append({
        "role": current_user.role,
        "user_id": current_user.user_id,
        "action": action,
        "remark": approval.remark or "",
        "timestamp": datetime.utcnow().isoformat()
    })

    await create_notification(
        user_id=leave["student_id"],
        title=f"Leave Application {leave['status']}",
        message=f"Your leave request for {leave['from_date']} to {leave['to_date']} was {leave['status']} by {current_user.role}.",
        notification_type="SUCCESS" if action == "APPROVE" else "WARNING"
    )

    return {"status": "success", "request": leave}
