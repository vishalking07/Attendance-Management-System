import hashlib
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.models.schemas import UserRole, TokenData
from app.services.auth_service import get_current_user
from app.services.ledger_service import create_attendance_block
from app.services.notification_service import create_notification, log_audit_event
from app.routes.users_data import mock_users_db, mock_attendance_db

router = APIRouter(prefix="/smart-pass", tags=["Smart Pass & Faculty Scanner"])

SALT_SECRET = "bioxai_smart_pass_secret_salt_2026"

class VerifySmartPassRequest(BaseModel):
    student_id: str
    pass_code: str
    scanner_location: Optional[str] = "Lecture Hall CS-301"

def generate_current_totp(student_id: str) -> tuple[str, int]:
    """
    Generates a deterministic 6-digit TOTP code changing every 30 seconds.
    Returns (totp_code, seconds_remaining).
    """
    current_time = int(time.time())
    time_step = current_time // 30
    seconds_remaining = 30 - (current_time % 30)

    raw = f"{student_id}:{time_step}:{SALT_SECRET}"
    hash_digest = hashlib.sha256(raw.encode()).hexdigest()
    code_int = int(hash_digest[:8], 16) % 1000000
    return f"{code_int:06d}", seconds_remaining

@router.get("/token/{student_id}")
async def get_student_smart_pass(
    student_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    code, seconds_left = generate_current_totp(student_id)

    return {
        "student_id": student["id"],
        "student_name": student["name"],
        "student_email": student["email"],
        "department_id": student.get("department_id", "CSE"),
        "dynamic_pass_code": code,
        "seconds_remaining": seconds_left,
        "qr_payload": f"BIOXAI://PASS/{student_id}/{code}",
        "pass_status": "ACTIVE_SECURE",
        "issued_at": datetime.utcnow().isoformat()
    }

@router.post("/verify")
async def verify_smart_pass_and_checkin(
    payload: VerifySmartPassRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Faculty / Mentor scans the student dynamic Smart Pass QR or inputs the 6-digit code.
    Verifies time validity and marks attendance instantly.
    """
    student = next((u for u in mock_users_db.values() if u["id"] == payload.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    expected_code, _ = generate_current_totp(payload.student_id)
    # Also allow immediate previous 30s window to prevent edge-of-second scan failures
    current_time = int(time.time())
    prev_time_step = (current_time // 30) - 1
    raw_prev = f"{payload.student_id}:{prev_time_step}:{SALT_SECRET}"
    prev_code = f"{int(hashlib.sha256(raw_prev.encode()).hexdigest()[:8], 16) % 1000000:06d}"

    cleaned_input = payload.pass_code.strip()
    if cleaned_input not in [expected_code, prev_code]:
        raise HTTPException(
            status_code=400,
            detail="Smart Pass verification failed: Expired or invalid dynamic TOTP security code."
        )

    today_str = datetime.now().strftime("%Y-%m-%d")
    record_id = f"att_{len(mock_attendance_db) + 1}"

    new_record = {
        "id": record_id,
        "student_id": student["id"],
        "student_name": student["name"],
        "department_id": student.get("department_id", "dept_cs"),
        "date": today_str,
        "status": "PRESENT",
        "confidence_score": 1.0,
        "verification_method": "FACULTY_SMART_PASS_SCAN",
        "marked_at": datetime.utcnow().isoformat(),
        "verified_by_faculty_id": current_user.user_id,
        "location": payload.scanner_location
    }

    mock_attendance_db.append(new_record)

    # Append to Cryptographic Ledger
    ledger_block = create_attendance_block(new_record)

    await create_notification(
        user_id=student["id"],
        title="Smart Pass Attendance Verified",
        message=f"Your dynamic Smart Pass was scanned and verified by faculty at {payload.scanner_location}.",
        notification_type="SUCCESS"
    )

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="FACULTY_SMART_PASS_VERIFICATION",
        target=student["id"],
        details=f"Verified dynamic pass code {cleaned_input} at {payload.scanner_location}. Ledger Block #{ledger_block['block_height']}"
    )

    return {
        "status": "VERIFIED_PRESENT",
        "student_name": student["name"],
        "student_id": student["id"],
        "marked_at": new_record["marked_at"],
        "ledger_block_height": ledger_block["block_height"],
        "ledger_block_hash": ledger_block["block_hash"][:16] + "...",
        "message": f"Successfully verified {student['name']} via Dynamic Smart Pass!"
    }
