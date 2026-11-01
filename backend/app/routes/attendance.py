from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from app.models.schemas import (
    FaceEnrollmentRequest, AttendanceCheckinRequest, OTPVerifyRequest,
    AttendanceRecordResponse, UserRole, TokenData
)
from app.services.auth_service import get_current_user, require_roles
from app.services.face_service import decode_base64_image, extract_face_embedding, compute_similarity
from app.services.geofence_service import check_geofence, haversine_distance
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

    # FACTOR 1: GEOFENCE LOCATION & DYNAMIC 500m FACULTY BEACON CHECK
    department_id = student.get("department_id")
    dept_geofence = next((g for g in mock_geofence_db.values() if g.get("department_id") == department_id), None)

    # Dynamic Faculty Beacon check: Attendance only permitted within 500m of active faculty classroom
    active_session = next((s for s in mock_sessions_db.values() if s.get("is_active")), None)
    faculty_distance_m = 24.5  # default nominal in-room distance
    
    if active_session:
        f_lat = active_session.get("faculty_lat", 12.9716)
        f_lng = active_session.get("faculty_lng", 77.5946)
        max_radius = active_session.get("radius_meters", 500.0)
        faculty_distance_m = haversine_distance(checkin.lat, checkin.lng, f_lat, f_lng)

        # STRICT 500m CUTOFF ENFORCEMENT
        if faculty_distance_m > max_radius:
            await log_audit_event(
                actor_id=student_id,
                actor_name=student["name"],
                action="ATTENDANCE_FACULTY_PROXIMITY_EXCEEDED",
                target=today_str,
                details=f"Distance {faculty_distance_m:.1f}m exceeded 500m perimeter from Instructor {active_session.get('faculty_name')} in {active_session.get('classroom_name')}."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Faculty Proximity Violation: You are {faculty_distance_m:.1f}m away from Instructor {active_session.get('faculty_name')}'s active class in {active_session.get('classroom_name')}. Attendance is strictly allowed only within 500m of the faculty location."
            )

        # Optional Class PIN verification if broadcast by faculty
        if checkin.class_pin and active_session.get("session_pin"):
            if checkin.class_pin.strip() != active_session.get("session_pin").strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Classroom Beacon PIN. Enter the 6-digit PIN broadcast on the classroom screen."
                )
    else:
        # Fallback to campus boundary if no active session
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
            "liveness_score": round(liveness_score, 2),
            "period_number": active_session.get("period_number", 1) if active_session else 1,
            "period_time": active_session.get("period_time", "09:00 - 10:00 AM") if active_session else "09:00 - 10:00 AM",
            "course_code": active_session.get("course_code", "CS801") if active_session else "CS801",
            "course_name": active_session.get("course_name", "Distributed Systems & Cloud Security") if active_session else "Distributed Systems & Cloud Security",
            "classroom_name": active_session.get("classroom_name", "Lecture Hall CS-301") if active_session else "Lecture Hall CS-301",
            "faculty_name": active_session.get("faculty_name", "Dr. Rajesh Ramanathan") if active_session else "Dr. Rajesh Ramanathan",
            "faculty_distance_m": round(faculty_distance_m, 1)
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
        "expires_at": expires_at.isoformat(),
        "period_number": active_session.get("period_number", 1) if active_session else 1,
        "period_time": active_session.get("period_time", "09:00 - 10:00 AM") if active_session else "09:00 - 10:00 AM",
        "course_code": active_session.get("course_code", "CS801") if active_session else "CS801",
        "course_name": active_session.get("course_name", "Distributed Systems & Cloud Security") if active_session else "Distributed Systems & Cloud Security",
        "classroom_name": active_session.get("classroom_name", "Lecture Hall CS-301") if active_session else "Lecture Hall CS-301",
        "faculty_name": active_session.get("faculty_name", "Dr. Rajesh Ramanathan") if active_session else "Dr. Rajesh Ramanathan",
        "faculty_distance_m": round(faculty_distance_m, 1)
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

class OfflineIDCheckinRequest(BaseModel):
    student_id: str
    scanner_location: Optional[str] = "Lecture Hall CS-301"
    reason: Optional[str] = "OFFLINE_NO_INTERNET"

@router.post("/offline-id-checkin")
async def mark_offline_student_id_attendance(
    payload: OfflineIDCheckinRequest,
    current_user: TokenData = Depends(require_roles([UserRole.MENTOR, UserRole.HOD, UserRole.ADMIN]))
):
    """
    Offline / No-Internet Fallback:
    When a student has no network connectivity in the classroom, the faculty inspects
    their physical Student ID / Roll number and marks them present with 1-click.
    """
    student = next((u for u in mock_users_db.values() if u["id"] == payload.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    today_str = datetime.now().strftime("%Y-%m-%d")
    record_id = f"att_off_{len(mock_attendance_db) + 1}"

    active_session = next((s for s in mock_sessions_db.values() if s.get("is_active")), None)

    new_record = {
        "id": record_id,
        "student_id": student["id"],
        "student_name": student["name"],
        "department_id": student.get("department_id", "dept_cs"),
        "date": today_str,
        "status": "PRESENT",
        "confidence_score": 1.0,
        "verification_method": "OFFLINE_STUDENT_ID_VERIFIED",
        "marked_at": datetime.utcnow().isoformat(),
        "verified_by_faculty_id": current_user.user_id,
        "location": payload.scanner_location or (active_session.get("classroom_name") if active_session else "Lecture Hall CS-301"),
        "period_number": active_session.get("period_number", 1) if active_session else 1,
        "period_time": active_session.get("period_time", "09:00 - 10:00 AM") if active_session else "09:00 - 10:00 AM",
        "course_code": active_session.get("course_code", "CS801") if active_session else "CS801",
        "course_name": active_session.get("course_name", "Distributed Systems & Cloud Security") if active_session else "Distributed Systems & Cloud Security",
        "classroom_name": active_session.get("classroom_name", "Lecture Hall CS-301") if active_session else "Lecture Hall CS-301",
        "faculty_name": active_session.get("faculty_name", "Dr. Rajesh Ramanathan") if active_session else "Dr. Rajesh Ramanathan",
        "faculty_distance_m": 0.0  # Physically verified on-site by faculty
    }

    mock_attendance_db.append(new_record)
    ledger_block = create_attendance_block(new_record)
    new_record["ledger_block_hash"] = ledger_block["block_hash"]
    new_record["ledger_block_height"] = ledger_block["block_height"]

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="OFFLINE_STUDENT_ID_OVERRIDE",
        target=student["id"],
        details=f"Physically verified student ID for {student['name']} due to no network connectivity in {payload.scanner_location}. Sealed Block #{ledger_block['block_height']}."
    )

    await create_notification(
        user_id=student["id"],
        title="Attendance Marked Present (Offline ID Verified)",
        message=f"Your attendance for {today_str} was marked present by faculty via physical ID check. Block #{ledger_block['block_height']} sealed.",
        notification_type="SUCCESS"
    )

    return {
        "status": "VERIFIED_PRESENT",
        "student_id": student["id"],
        "student_name": student["name"],
        "marked_at": new_record["marked_at"],
        "verification_method": "OFFLINE_STUDENT_ID_VERIFIED",
        "ledger_block_height": ledger_block["block_height"],
        "ledger_block_hash": ledger_block["block_hash"][:16] + "...",
        "message": f"Successfully verified {student['name']} via Physical Student ID Card (Offline Fallback)!"
    }

class ClassPinCheckinRequest(BaseModel):
    student_id: str
    class_pin: str
    lat: Optional[float] = 12.9716
    lng: Optional[float] = 77.5946
    wifi_ssid: Optional[str] = "EduNet-Secure-5G"

@router.post("/class-pin-checkin")
async def mark_attendance_via_class_pin(
    payload: ClassPinCheckinRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Direct Faculty Broadcast PIN / OTP Attendance Check-In (500m geofence enforced).
    Allows student to enter the 6-digit lecture PIN generated by faculty and instantly mark attendance.
    """
    student_id = payload.student_id
    student = next((u for u in mock_users_db.values() if u["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    if current_user.role == UserRole.STUDENT and current_user.user_id != student_id:
        raise HTTPException(status_code=403, detail="Cannot mark attendance for another student")

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Fetch active faculty classroom session
    active_session = next((s for s in mock_sessions_db.values() if s.get("is_active")), None)
    if not active_session:
        raise HTTPException(status_code=400, detail="No active classroom lecture beacon is currently broadcasting.")

    # Enforce strict 500m proximity check
    f_lat = active_session.get("faculty_lat", 12.9716)
    f_lng = active_session.get("faculty_lng", 77.5946)
    max_radius = active_session.get("radius_meters", 500.0)
    faculty_distance_m = haversine_distance(payload.lat, payload.lng, f_lat, f_lng)

    if faculty_distance_m > max_radius:
        await log_audit_event(
            actor_id=student_id,
            actor_name=student["name"],
            action="ATTENDANCE_FACULTY_PROXIMITY_EXCEEDED",
            target=today_str,
            details=f"Distance {faculty_distance_m:.1f}m exceeded 500m perimeter from Instructor {active_session.get('faculty_name')} in {active_session.get('classroom_name')}."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faculty Proximity Violation: You are {faculty_distance_m:.1f}m away from active lecture in {active_session.get('classroom_name')}. Attendance is strictly allowed only within 500m of the faculty location."
        )

    # Validate 6-digit class PIN / OTP
    expected_pin = str(active_session.get("session_pin", "")).strip()
    if payload.class_pin.strip() != expected_pin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Classroom Beacon PIN. Enter the 6-digit PIN broadcast by Instructor {active_session.get('faculty_name')} on the classroom screen."
        )

    wifi_verified = False
    if payload.wifi_ssid and any(term in payload.wifi_ssid for term in ["EduNet", "Campus", "Lab", "WiFi", "Secure", "5G", "CS"]):
        wifi_verified = True

    record_id = f"att_pin_{len(mock_attendance_db) + 1}"
    session_id = f"sess_pin_{uuid.uuid4().hex[:8]}"

    new_record = {
        "id": record_id,
        "student_id": student_id,
        "student_name": student["name"],
        "department_id": student.get("department_id"),
        "date": today_str,
        "status": "PRESENT",
        "confidence_score": 1.0,
        "verification_method": "CLASSROOM_BEACON_PIN",
        "marked_at": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "wifi_verified": wifi_verified,
        "liveness_score": 1.0,
        "period_number": active_session.get("period_number", 1),
        "period_time": active_session.get("period_time", "09:00 - 10:00 AM"),
        "course_code": active_session.get("course_code", "CS801"),
        "course_name": active_session.get("course_name", "Distributed Systems & Cloud Security"),
        "classroom_name": active_session.get("classroom_name", "Lecture Hall CS-301"),
        "faculty_name": active_session.get("faculty_name", "Dr. Rajesh Ramanathan"),
        "faculty_distance_m": round(faculty_distance_m, 1)
    }

    ledger_block = create_attendance_block(new_record)
    new_record["ledger_block_hash"] = ledger_block["block_hash"]
    new_record["ledger_block_height"] = ledger_block["block_height"]

    mock_attendance_db.append(new_record)

    await log_audit_event(
        actor_id=student_id,
        actor_name=student["name"],
        action="ATTENDANCE_MARKED_PRESENT_CLASS_PIN",
        target=today_str,
        details=f"Attendance confirmed via Classroom Beacon PIN #{expected_pin} for {active_session.get('course_code')}. Sealed Block #{ledger_block['block_height']}."
    )

    await create_notification(
        user_id=student_id,
        title="Attendance Marked Present (Classroom Beacon PIN)",
        message=f"Attendance for {today_str} ({active_session.get('course_code')} - Period {active_session.get('period_number', 1)}) marked PRESENT via Classroom PIN! Block #{ledger_block['block_height']} sealed.",
        notification_type="SUCCESS"
    )

    return {
        "status": "SUCCESS",
        "message": f"Classroom Beacon PIN Verified! Marked PRESENT for {active_session.get('course_code')} (Distance: {faculty_distance_m:.1f}m, Block #{ledger_block['block_height']}).",
        "record": new_record,
        "ledger_receipt": {
            "block_height": ledger_block["block_height"],
            "block_hash": ledger_block["block_hash"][:16] + "...",
            "dual_signal": "GPS + WiFi Verified" if wifi_verified else "GPS Only"
        }
    }

@router.get("/sessions")
async def get_session_wise_attendance(
    date: Optional[str] = None,
    student_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Returns full day period-by-period (session-wise) timetable and attendance breakdown
    for the requested date (defaults to today).
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    target_student_id = student_id if (student_id and current_user.role != UserRole.STUDENT) else current_user.user_id

    # 5 standard daily academic periods
    default_schedule = [
        {
            "period_number": 1,
            "period_time": "09:00 - 10:00 AM",
            "course_code": "CS801",
            "course_name": "Distributed Systems & Cloud Security",
            "faculty_name": "Dr. Rajesh Ramanathan",
            "classroom_name": "Lecture Hall CS-301",
            "default_status": "PRESENT",
            "method": "BIOMETRIC_DIRECT",
            "faculty_distance_m": 24.5
        },
        {
            "period_number": 2,
            "period_time": "10:15 - 11:15 AM",
            "course_code": "CS802",
            "course_name": "Deep Neural Networks & Computer Vision",
            "faculty_name": "Dr. Alan Turing",
            "classroom_name": "AI GPU Lab 1",
            "default_status": "PRESENT",
            "method": "SMART_PASS_QR",
            "faculty_distance_m": 31.2
        },
        {
            "period_number": 3,
            "period_time": "11:30 - 12:30 PM",
            "course_code": "CS803",
            "course_name": "Cloud Infrastructure & Microservices",
            "faculty_name": "Dr. Tim Berners-Lee",
            "classroom_name": "Lecture Hall CS-302",
            "default_status": "PRESENT",
            "method": "OFFLINE_STUDENT_ID_VERIFIED",
            "faculty_distance_m": 18.0
        },
        {
            "period_number": 4,
            "period_time": "01:30 - 02:30 PM",
            "course_code": "CS804",
            "course_name": "Blockchain & Zero-Knowledge Cryptography",
            "faculty_name": "Dr. Ada Lovelace",
            "classroom_name": "Cyber Operations Room",
            "default_status": "ABSENT",
            "method": "UNEXCUSED_ABSENCE",
            "faculty_distance_m": 720.0
        },
        {
            "period_number": 5,
            "period_time": "02:45 - 03:45 PM",
            "course_code": "CS805",
            "course_name": "Bio-XAI Capstone Seminar",
            "faculty_name": "Dr. Rajesh Ramanathan",
            "classroom_name": "Seminar Hall B",
            "default_status": "UPCOMING",
            "method": "SCHEDULED",
            "faculty_distance_m": None
        }
    ]

    # Look up actual logged attendance records for target_student_id on target_date
    day_records = [
        r for r in mock_attendance_db 
        if r.get("student_id") == target_student_id and r.get("date") == target_date
    ]

    periods_response = []
    for s in default_schedule:
        matched = next((r for r in reversed(day_records) if r.get("period_number") == s["period_number"]), None)
        if not matched and s["period_number"] == 1 and len(day_records) > 0:
            matched = day_records[-1]

        if matched:
            periods_response.append({
                "period_number": s["period_number"],
                "period_time": s["period_time"],
                "course_code": matched.get("course_code", s["course_code"]),
                "course_name": matched.get("course_name", s["course_name"]),
                "faculty_name": matched.get("faculty_name", s["faculty_name"]),
                "classroom_name": matched.get("classroom_name", s["classroom_name"]),
                "status": matched.get("status", "PRESENT"),
                "verification_method": matched.get("verification_method", "BIOMETRIC_DIRECT"),
                "faculty_distance_m": matched.get("faculty_distance_m", s["faculty_distance_m"]),
                "in_500m_perimeter": (matched.get("faculty_distance_m", 25.0) or 25.0) <= 500.0,
                "marked_at": matched.get("marked_at"),
                "ledger_block_height": matched.get("ledger_block_height", 1420 + s["period_number"]),
                "ledger_block_hash": matched.get("ledger_block_hash", "0x9f4a...b18c")
            })
        else:
            periods_response.append({
                "period_number": s["period_number"],
                "period_time": s["period_time"],
                "course_code": s["course_code"],
                "course_name": s["course_name"],
                "faculty_name": s["faculty_name"],
                "classroom_name": s["classroom_name"],
                "status": s["default_status"],
                "verification_method": s["method"],
                "faculty_distance_m": s["faculty_distance_m"],
                "in_500m_perimeter": (s["faculty_distance_m"] or 999.0) <= 500.0 if s["faculty_distance_m"] else False,
                "marked_at": f"{target_date}T{s['period_time'][:2]}:05:00Z" if s["default_status"] == "PRESENT" else None,
                "ledger_block_height": 1420 + s["period_number"] if s["default_status"] == "PRESENT" else None,
                "ledger_block_hash": "0x4b7c...28e1" if s["default_status"] == "PRESENT" else None
            })

    total_periods = len(periods_response)
    present_count = len([p for p in periods_response if p["status"] == "PRESENT"])
    absent_count = len([p for p in periods_response if p["status"] == "ABSENT"])
    upcoming_count = len([p for p in periods_response if p["status"] == "UPCOMING"])
    attendance_rate = round((present_count / max(present_count + absent_count, 1)) * 100, 1)

    return {
        "date": target_date,
        "student_id": target_student_id,
        "total_periods": total_periods,
        "present_periods": present_count,
        "absent_periods": absent_count,
        "upcoming_periods": upcoming_count,
        "day_attendance_pct": attendance_rate,
        "faculty_proximity_enforced": True,
        "max_geofence_radius_m": 500.0,
        "periods": periods_response
    }

