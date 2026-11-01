from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import random
from app.models.schemas import GeofenceZoneCreate, GeofenceZoneResponse, UserRole, TokenData
from app.services.auth_service import get_current_user, require_roles
from app.services.notification_service import log_audit_event
from app.routes.users_data import mock_geofence_db, mock_sessions_db

router = APIRouter(prefix="/geofence", tags=["Geofence"])

class BeaconUpdateRequest(BaseModel):
    classroom_name: str
    faculty_lat: float
    faculty_lng: float
    course_code: Optional[str] = "CS801"
    course_name: Optional[str] = "Distributed Systems & Cloud Security"
    radius_meters: Optional[float] = 500.0
    period_number: Optional[int] = 1
    period_time: Optional[str] = "09:00 - 10:00 AM"
    session_pin: Optional[str] = None

@router.get("", response_model=List[GeofenceZoneResponse])
async def list_geofence_zones(current_user: TokenData = Depends(get_current_user)):
    return list(mock_geofence_db.values())

@router.get("/active-session")
async def get_active_classroom_session(current_user: TokenData = Depends(get_current_user)):
    """
    Returns the dynamic faculty-centric active lecture session beacon (500m geofence).
    """
    active = next((s for s in mock_sessions_db.values() if s.get("is_active")), None)
    if not active:
        active = {
            "session_id": "sess_live_default",
            "faculty_id": "usr_mentor1",
            "faculty_name": "Dr. Rajesh Ramanathan (Faculty Advisor)",
            "department_id": "dept_cs",
            "course_code": "CS801",
            "course_name": "Distributed Systems & Cloud Security",
            "period_number": 1,
            "period_time": "09:00 - 10:00 AM",
            "classroom_name": "Lecture Hall CS-301",
            "faculty_lat": 12.9716,
            "faculty_lng": 77.5946,
            "radius_meters": 500.0,
            "session_pin": "482910",
            "qr_payload": "BIOXAI://CLASS/CS801/CS-301/482910",
            "is_active": True,
            "started_at": datetime.utcnow().isoformat()
        }
        mock_sessions_db["sess_live_default"] = active

    return active

@router.post("/beacon/update")
async def update_faculty_beacon(
    payload: BeaconUpdateRequest,
    current_user: TokenData = Depends(require_roles([UserRole.MENTOR, UserRole.HOD, UserRole.ADMIN]))
):
    """
    Faculty / Mentor updates their live lecture room and GPS anchor point.
    Anchors attendance strictly within 500 meters of this dynamic location.
    """
    session_id = f"sess_{current_user.user_id}_{datetime.now().strftime('%H%M%S')}"
    new_pin = payload.session_pin or f"{random.randint(100000, 999999)}"
    
    updated_session = {
        "session_id": session_id,
        "faculty_id": current_user.user_id,
        "faculty_name": getattr(current_user, 'name', 'Dr. Rajesh Ramanathan'),
        "department_id": getattr(current_user, 'department_id', 'dept_cs'),
        "course_code": payload.course_code or "CS801",
        "course_name": payload.course_name or "Distributed Systems & Cloud Security",
        "period_number": payload.period_number or 1,
        "period_time": payload.period_time or "09:00 - 10:00 AM",
        "classroom_name": payload.classroom_name,
        "faculty_lat": payload.faculty_lat,
        "faculty_lng": payload.faculty_lng,
        "radius_meters": payload.radius_meters or 500.0,
        "session_pin": new_pin,
        "qr_payload": f"BIOXAI://CLASS/{payload.course_code}/{payload.classroom_name.replace(' ', '_')}/{new_pin}",
        "is_active": True,
        "started_at": datetime.utcnow().isoformat()
    }

    # Mark other sessions inactive and set this one active
    for s in mock_sessions_db.values():
        s["is_active"] = False

    mock_sessions_db[session_id] = updated_session

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="FACULTY_GEOFENCE_BEACON_BROADCAST",
        target=payload.classroom_name,
        details=f"Live 500m Beacon anchored at ({payload.faculty_lat:.4f}, {payload.faculty_lng:.4f}) in {payload.classroom_name}. Course: {payload.course_code}, PIN: {new_pin}"
    )

    return {
        "status": "BEACON_ACTIVE",
        "message": f"Live 500m geofence beacon active for {payload.classroom_name}! Students must be within {updated_session['radius_meters']}m.",
        "beacon": updated_session
    }

@router.post("", response_model=GeofenceZoneResponse)
async def create_geofence_zone(
    zone_data: GeofenceZoneCreate,
    current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))
):
    new_id = f"geo_{len(mock_geofence_db) + 1}"
    coords_dict = [{"lat": c.lat, "lng": c.lng} for c in zone_data.coordinates]
    zone_entry = {
        "id": new_id,
        "name": zone_data.name,
        "department_id": zone_data.department_id,
        "coordinates": coords_dict,
        "center_lat": zone_data.center_lat,
        "center_lng": zone_data.center_lng,
        "radius_meters": zone_data.radius_meters
    }
    mock_geofence_db[new_id] = zone_entry
    return zone_entry

