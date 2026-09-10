from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from app.models.schemas import CorrectionRequestCreate, ApprovalAction, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles
from app.services.notification_service import create_notification, log_audit_event
from app.routes.users_data import mock_corrections_db, mock_attendance_db, mock_users_db

router = APIRouter(prefix="/corrections", tags=["Corrections"])

@router.get("")
async def list_corrections(
    status_filter: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    corrections = list(mock_corrections_db)

    # RBAC Scoping
    if current_user.role == UserRole.STUDENT:
        corrections = [c for c in corrections if c["student_id"] == current_user.user_id]
    elif current_user.role == UserRole.MENTOR:
        mentees = [u["id"] for u in mock_users_db.values() if u.get("mentor_id") == current_user.user_id]
        corrections = [c for c in corrections if c["student_id"] in mentees]
    elif current_user.role == UserRole.HOD:
        corrections = [c for c in corrections if c.get("department_id") == current_user.department_id]

    if status_filter:
        corrections = [c for c in corrections if c["status"] == status_filter]

    return corrections

@router.post("")
async def create_correction_request(
    correction: CorrectionRequestCreate,
    current_user: TokenData = Depends(require_roles([UserRole.STUDENT]))
):
    student_id = current_user.user_id
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    
    new_id = f"corr_{len(mock_corrections_db) + 1}"
    entry = {
        "id": new_id,
        "student_id": student_id,
        "student_name": student["name"] if student else "Student",
        "department_id": current_user.department_id,
        "date": correction.date,
        "reason": correction.reason,
        "claimed_time": correction.claimed_time,
        "evidence_photo_base64": correction.evidence_photo_base64,
        "status": "PENDING",  # PENDING, APPROVED, REJECTED, ESCALATED
        "created_at": datetime.utcnow().isoformat(),
        "approval_trail": []
    }
    mock_corrections_db.append(entry)

    # Notify Mentor
    if student and student.get("mentor_id"):
        await create_notification(
            user_id=student["mentor_id"],
            title="New Attendance Correction Request",
            message=f"{student['name']} submitted a correction request for {correction.date}.",
            notification_type="INFO"
        )

    await log_audit_event(
        actor_id=student_id,
        actor_name=student["name"] if student else "Student",
        action="SUBMIT_CORRECTION_REQUEST",
        target=new_id,
        details=f"Correction requested for date {correction.date}: {correction.reason}"
    )

    return entry

@router.post("/approve")
async def review_correction_request(
    approval: ApprovalAction,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD, UserRole.MENTOR]))
):
    corr = next((c for c in mock_corrections_db if c["id"] == approval.request_id), None)
    if not corr:
        raise HTTPException(status_code=404, detail="Correction request not found")

    action = approval.action.upper()  # APPROVE, REJECT, ESCALATE
    corr["status"] = "APPROVED" if action == "APPROVE" else ("REJECTED" if action == "REJECT" else "ESCALATED")

    trail_entry = {
        "role": current_user.role,
        "user_id": current_user.user_id,
        "action": action,
        "remark": approval.remark or "",
        "timestamp": datetime.utcnow().isoformat()
    }
    corr.get("approval_trail", []).append(trail_entry)

    # If APPROVED -> Update attendance record to PRESENT
    if action == "APPROVE":
        att_record = next((a for a in mock_attendance_db if a["student_id"] == corr["student_id"] and a["date"] == corr["date"]), None)
        if att_record:
            att_record["status"] = "PRESENT"
            att_record["verification_method"] = "MANUAL_CORRECTION"
        else:
            mock_attendance_db.append({
                "id": f"att_{len(mock_attendance_db) + 1}",
                "student_id": corr["student_id"],
                "student_name": corr["student_name"],
                "department_id": corr["department_id"],
                "date": corr["date"],
                "status": "PRESENT",
                "confidence_score": 1.0,
                "verification_method": "MANUAL_CORRECTION",
                "marked_at": datetime.utcnow().isoformat()
            })

    # Notify student
    await create_notification(
        user_id=corr["student_id"],
        title=f"Correction Request {corr['status']}",
        message=f"Your attendance correction for {corr['date']} was {corr['status']} by {current_user.role}. Remark: {approval.remark or 'None'}",
        notification_type="SUCCESS" if action == "APPROVE" else "WARNING"
    )

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action=f"CORRECTION_{action}",
        target=corr["id"],
        details=f"Correction for student {corr['student_name']} on {corr['date']} mark {corr['status']}"
    )

    return {"status": "success", "request": corr}
