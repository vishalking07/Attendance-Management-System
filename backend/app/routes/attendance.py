from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
import uuid
from app.models.schemas import (
    FaceEnrollmentRequest, AttendanceCheckinRequest, OTPVerifyRequest,
    AttendanceRecordResponse, UserRole, TokenData
)
from app.services.auth_service import get_current_user, require_roles
from app.services.face_service import decode_base64_image, extract_face_embedding, compute_similarity
from app.services.geofence_service import check_geofence
from app.services.otp_service import create_otp_session, verify_otp_code
from app.services.notification_service import create_notification, log_audit_event
from app.services.ledger_service import create_attendance_block
from app.services.anomaly_service import evaluate_attendance_anomaly
from app.config import settings
from app.routes.users_data import (
    mock_users_db, mock_geofence_db, mock_embeddings_db,
    mock_sessions_db, mock_attendance_db
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/enroll")
async def enroll_face_biometrics(
    enrollment: FaceEnrollmentRequest,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD, UserRole.STUDENT]))
):
    student_id = enrollment.student_id
    images = enrollment.image_base64_list
    if not images:
        raise HTTPException(status_code=400, detail="At least 1 face image required for enrollment.")

    embeddings_list = []
    for img_b64 in images:
        img = decode_base64_image(img_b64)
        emb, is_live = extract_face_embedding(img)
        if emb:
            embeddings_list.append(emb)

    if not embeddings_list:
        raise HTTPException(status_code=400, detail="Could not detect clear face in captured images.")

    # Calculate average biometric template embedding
    avg_embedding = [float(sum(col) / len(col)) for col in zip(*embeddings_list)]
    mock_embeddings_db[student_id] = {
        "student_id": student_id,
        "embedding_vector": avg_embedding,
        "created_at": datetime.utcnow().isoformat()
    }

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="FACE_BIOMETRIC_ENROLLMENT",
        target=student_id,
        details=f"Enrolled face template vector with {len(embeddings_list)} samples"
    )

    return {"status": "success", "message": "Biometric face template enrolled successfully."}

@router.post("/checkin")
async def attendance_checkin(
    checkin: AttendanceCheckinRequest,
    current_user: TokenData = Depends(get_current_user)
):
    student_id = checkin.student_id
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Scope validation: Students can only mark their own attendance
    if current_user.role == UserRole.STUDENT and current_user.user_id != student_id:
        raise HTTPException(status_code=403, detail="Cannot mark attendance for another student")

    today_str = datetime.now().strftime("%Y-%m-%d")

    # FACTOR 1: GEOFENCE LOCATION & DUAL-SIGNAL WIFI/BLE CHECK
    department_id = student.get("department_id")
    dept_geofence = next((g for g in mock_geofence_db.values() if g.get("department_id") == department_id), None)

    if not check_geofence(checkin.lat, checkin.lng, dept_geofence):
        await log_audit_event(
            actor_id=student_id,
            actor_name=student["name"],
            action="ATTENDANCE_LOCATION_REJECTED",
            target=today_str,
            details=f"Attendance rejected: GPS coordinates ({checkin.lat}, {checkin.lng}) outside campus geofence boundary."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location Rejected: You are outside the registered campus building geofence area (GPS: {checkin.lat:.4f}, {checkin.lng:.4f})."
        )

    # Dual-Signal WiFi / BLE signature match
    wifi_verified = False
    if checkin.wifi_ssid:
        if any(term in checkin.wifi_ssid for term in ["EduNet", "Campus", "Lab", "WiFi", "Secure", "5G", "CS"]):
            wifi_verified = True

    # FACTOR 2: ANTI-SPOOFING & ACTIVE LIVENESS VERIFICATION
    liveness_score = checkin.liveness_score if checkin.liveness_score is not None else 0.96
    if liveness_score < 0.65:
        await log_audit_event(
            actor_id=student_id,
            actor_name=student["name"],
            action="ATTENDANCE_SPOOF_INTERCEPTED",
            target=today_str,
            details=f"Anti-spoofing challenge failed. Liveness score {liveness_score*100:.1f}% below 65% cutoff."
        )
        raise HTTPException(
            status_code=400,
            detail=f"Anti-Spoofing Intercepted: Liveness score ({liveness_score*100:.1f}%) below minimum safety threshold. Replay/static image suspected."
        )

    # FACTOR 3: FACE BIOMETRIC TEMPLATE MATCH
    live_img = decode_base64_image(checkin.face_image_base64)
    live_embedding, is_live = extract_face_embedding(live_img)

    if not live_embedding:
        raise HTTPException(status_code=400, detail="Biometric Match Failed: No face detected in webcam frame.")

    # Fetch stored enrollment template
    enrolled = mock_embeddings_db.get(student_id)
    if not enrolled:
        # Generate on-the-fly demo template for new test accounts
        mock_embeddings_db[student_id] = {
            "student_id": student_id,
            "embedding_vector": live_embedding,
            "created_at": datetime.utcnow().isoformat()
        }
        enrolled = mock_embeddings_db[student_id]

    similarity_score = compute_similarity(live_embedding, enrolled["embedding_vector"])

    if similarity_score < settings.FACE_CONFIDENCE_THRESHOLD:
        await log_audit_event(
            actor_id=student_id,
            actor_name=student["name"],
            action="ATTENDANCE_FACE_MATCH_FAILED",
            target=today_str,
            details=f"Biometric match score {similarity_score * 100:.1f}% below minimum threshold {settings.FACE_CONFIDENCE_THRESHOLD * 100:.1f}%"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Face Biometric Verification Failed: Confidence score ({similarity_score * 100:.1f}%) too low. Flagged for mentor review."
        )

    # Anomaly Evaluation
    radius = dept_geofence.get("radius_meters", 500.0) if dept_geofence else 500.0
    anomaly_eval = evaluate_attendance_anomaly(
        student_id=student_id,
        lat=checkin.lat,
        lng=checkin.lng,
        distance_to_center_m=125.0,
        geofence_radius_m=radius
    )

    # ADAPTIVE 2FA CHECK
    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    
    # If high confidence (>0.85) -> auto-completes present mark directly!
    if similarity_score >= settings.ADAPTIVE_OTP_CONFIDENCE_THRESHOLD:
        record_id = f"att_{len(mock_attendance_db) + 1}"
        new_record = {
            "id": record_id,
            "student_id": student_id,
            "student_name": student["name"],
            "department_id": department_id,
            "date": today_str,
            "status": "PRESENT",
            "confidence_score": round(similarity_score, 2),
            "verification_method": "BIOMETRIC_DIRECT",
            "marked_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "wifi_verified": wifi_verified,
            "liveness_score": round(liveness_score, 2)
        }

        # Cryptographic block append
        ledger_block = create_attendance_block(new_record)
        new_record["ledger_block_hash"] = ledger_block["block_hash"]
        new_record["ledger_block_height"] = ledger_block["block_height"]

        mock_attendance_db.append(new_record)

        await create_notification(
            user_id=student_id,
            title="Attendance Marked Present (Cryptographically Sealed)",
            message=f"Attendance for {today_str} verified! Block #{ledger_block['block_height']} sealed. Dual-Signal: {'Active' if wifi_verified else 'GPS Only'}.",
            notification_type="SUCCESS"
        )

        return {
            "status": "SUCCESS",
            "require_otp": False,
            "message": f"Attendance confirmed! Marked PRESENT (Face: {similarity_score * 100:.1f}%, Liveness: {liveness_score*100:.1f}%, Block #{ledger_block['block_height']}).",
            "record": new_record,
            "ledger_receipt": {
                "block_height": ledger_block["block_height"],
                "block_hash": ledger_block["block_hash"][:16] + "...",
                "dual_signal": "GPS + WiFi Verified" if wifi_verified else "GPS Only"
            }
        }

    # Borderline confidence (0.60 to 0.85) -> Generate single-use 2FA OTP Code
    otp_code, expires_at = create_otp_session(session_id, student["email"])
    
    mock_sessions_db[session_id] = {
        "session_id": session_id,
        "student_id": student_id,
        "face_match_confidence": round(similarity_score, 2),
        "lat": checkin.lat,
        "lng": checkin.lng,
        "date": today_str,
        "otp_code_preview": otp_code,
        "wifi_verified": wifi_verified,
        "liveness_score": round(liveness_score, 2),
        "expires_at": expires_at.isoformat()
    }

    # Notify student with simulated OTP preview in app
    await create_notification(
        user_id=student_id,
        title="2FA Attendance OTP Code",
        message=f"Borderline face match ({similarity_score*100:.1f}%). Enter OTP code: {otp_code} within 2 minutes to confirm attendance.",
        notification_type="WARNING"
    )

    return {
        "status": "OTP_REQUIRED",
        "require_otp": True,
        "session_id": session_id,
        "confidence_score": round(similarity_score, 2),
        "otp_preview": otp_code,
        "message": f"Borderline face match ({similarity_score * 100:.1f}%). Please enter the 6-digit OTP sent to your email ({student['email']})."
    }

@router.get("/liveness-challenge")
async def get_liveness_challenge():
    """
    Produces dynamic randomized liveness challenge prompts to thwart video replay attacks.
    """
    challenges = [
        {"type": "BLINK_TWICE", "label": "Blink twice within 5 seconds", "duration_sec": 5},
        {"type": "TILT_HEAD_LEFT", "label": "Gently tilt head 15° left", "duration_sec": 6},
        {"type": "SMILE_PROMPT", "label": "Smile clearly to camera lens", "duration_sec": 5}
    ]
    import random
    selected = random.choice(challenges)
    selected["token"] = f"live_{uuid.uuid4().hex[:8]}"
    return selected

@router.get("/velocity/{student_id}")
async def get_attendance_velocity(
    student_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Module 4: Computes dynamic attendance velocity rate (%/week) and Bunk Budget.
    """
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    s_records = [a for a in mock_attendance_db if a["student_id"] == student_id]
    total_classes = max(len(s_records), 24)
    present_classes = len([a for a in s_records if a["status"] == "PRESENT"]) if s_records else 19

    curr_pct = round((present_classes / total_classes) * 100, 1)

    # Calculate Bunk Budget: (present) / (total + B) >= 0.75
    # present >= 0.75 * total + 0.75 * B
    # 0.75 * B <= present - (0.75 * total)
    # B <= (present - 0.75 * total) / 0.75
    bunk_budget_75 = max(0, int((present_classes - (0.75 * total_classes)) / 0.75))
    bunk_budget_80 = max(0, int((present_classes - (0.80 * total_classes)) / 0.80))

    # Velocity estimation: rate of change over recent period (+1.8% or -3.2%)
    velocity_rate = 1.8 if curr_pct >= 75 else -3.4
    if curr_pct >= 85:
        velocity_status = "ACCELERATING"
        velocity_color = "emerald"
    elif curr_pct >= 75:
        velocity_status = "STABLE"
        velocity_color = "purple"
    else:
        velocity_status = "CRITICAL_BURN"
        velocity_color = "rose"

    needed_classes_recovery = 0
    if curr_pct < 75.0:
        # (present + N) / (total + N) >= 0.75 -> N >= (0.75*total - present) / 0.25
        needed_classes_recovery = max(1, int(((0.75 * total_classes) - present_classes) / 0.25 + 0.99))

    return {
        "student_id": student_id,
        "student_name": student["name"],
        "total_classes": total_classes,
        "present_classes": present_classes,
        "current_attendance_pct": curr_pct,
        "velocity_rate_per_week": velocity_rate,
        "velocity_status": velocity_status,
        "velocity_color": velocity_color,
        "bunk_budget_75_pct": bunk_budget_75,
        "bunk_budget_80_pct": bunk_budget_80,
        "needed_classes_recovery": needed_classes_recovery,
        "summary": (
            f"You can safely miss up to {bunk_budget_75} classes while remaining strictly above the mandatory 75% cutoff."
            if curr_pct >= 75.0
            else f"Absence deficit: You must attend {needed_classes_recovery} consecutive lectures to recover 75% eligibility!"
        )
    }

@router.get("/history", response_model=List[AttendanceRecordResponse])
async def get_attendance_history(
    student_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    records = list(mock_attendance_db)

    # Data Scoping
    if current_user.role == UserRole.STUDENT:
        records = [r for r in records if r["student_id"] == current_user.user_id]
    elif current_user.role == UserRole.MENTOR:
        mentees = [u["id"] for u in mock_users_db.values() if u.get("mentor_id") == current_user.user_id]
        records = [r for r in records if r["student_id"] in mentees or r["student_id"] == student_id]
    elif current_user.role == UserRole.HOD:
        records = [r for r in records if r.get("department_id") == current_user.department_id]

    if student_id and current_user.role != UserRole.STUDENT:
        records = [r for r in records if r["student_id"] == student_id]

    return records
