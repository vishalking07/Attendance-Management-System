from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.models.schemas import OTPVerifyRequest, TokenData
from app.services.auth_service import get_current_user
from app.services.otp_service import verify_otp_code
from app.services.notification_service import create_notification, log_audit_event
from app.services.ledger_service import create_attendance_block
from app.routes.users_data import mock_sessions_db, mock_attendance_db, mock_users_db

router = APIRouter(prefix="/otp", tags=["OTP"])

@router.post("/verify")
async def verify_attendance_otp(
    verify_req: OTPVerifyRequest,
    current_user: TokenData = Depends(get_current_user)
):
    session_id = verify_req.session_id
    session = mock_sessions_db.get(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired attendance session.")

    student_id = session["student_id"]
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")

    # Validate OTP code
    success, message = verify_otp_code(session_id, verify_req.otp_code)
    if not success:
        await log_audit_event(
            actor_id=student_id,
            actor_name=student["name"],
            action="OTP_VERIFICATION_FAILED",
            target=session_id,
            details=f"Failed OTP verification attempt: {message}"
        )
        raise HTTPException(status_code=400, detail=message)

    # Retrieve active classroom session or fallback
    active_session = next((s for s in mock_sessions_db.values() if s.get("is_active")), None)

    # Mark Attendance PRESENT
    record_id = f"att_{len(mock_attendance_db) + 1}"
    today_str = session.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    new_record = {
        "id": record_id,
        "student_id": student_id,
        "student_name": student["name"],
        "department_id": student.get("department_id"),
        "date": today_str,
        "status": "PRESENT",
        "confidence_score": session.get("face_match_confidence", 0.75),
        "verification_method": "BIOMETRIC_OTP",
        "marked_at": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "wifi_verified": session.get("wifi_verified", False),
        "liveness_score": session.get("liveness_score", 0.95),
        "period_number": session.get("period_number") or (active_session.get("period_number", 1) if active_session else 1),
        "period_time": session.get("period_time") or (active_session.get("period_time", "09:00 - 10:00 AM") if active_session else "09:00 - 10:00 AM"),
        "course_code": session.get("course_code") or (active_session.get("course_code", "CS801") if active_session else "CS801"),
        "course_name": session.get("course_name") or (active_session.get("course_name", "Distributed Systems & Cloud Security") if active_session else "Distributed Systems & Cloud Security"),
        "classroom_name": session.get("classroom_name") or (active_session.get("classroom_name", "Lecture Hall CS-301") if active_session else "Lecture Hall CS-301"),
        "faculty_name": session.get("faculty_name") or (active_session.get("faculty_name", "Dr. Rajesh Ramanathan") if active_session else "Dr. Rajesh Ramanathan"),
        "faculty_distance_m": session.get("faculty_distance_m", 24.5)
    }

    # Append to Cryptographic Ledger
    ledger_block = create_attendance_block(new_record)
    new_record["ledger_block_hash"] = ledger_block["block_hash"]
    new_record["ledger_block_height"] = ledger_block["block_height"]

    mock_attendance_db.append(new_record)

    await log_audit_event(
        actor_id=student_id,
        actor_name=student["name"],
        action="ATTENDANCE_MARKED_PRESENT_OTP",
        target=today_str,
        details=f"Attendance confirmed via 2FA OTP for session {session_id}. Ledger Block #{ledger_block['block_height']}"
    )

    await create_notification(
        user_id=student_id,
        title="Attendance Confirmed via 2FA OTP",
        message=f"Attendance for {today_str} marked PRESENT after 2FA OTP verification.",
        notification_type="SUCCESS"
    )

    return {
        "status": "SUCCESS",
        "message": "2FA OTP verified successfully! Attendance marked PRESENT.",
        "record": new_record,
        "ledger_receipt": {
            "block_height": ledger_block["block_height"],
            "block_hash": ledger_block["block_hash"][:16] + "...",
            "dual_signal": "GPS + WiFi Verified" if session.get("wifi_verified") else "GPS Only"
        }
    }
