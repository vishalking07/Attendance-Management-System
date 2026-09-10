from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    HOD = "HOD"
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class TokenData(BaseModel):
    user_id: str
    role: UserRole
    department_id: Optional[str] = None
    mentor_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    department_id: Optional[str] = None
    mentor_id: Optional[str] = None
    profile_photo: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    mentor_id: Optional[str] = None
    profile_photo: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: Optional[datetime] = None

# --- DEPARTMENT SCHEMAS ---
class DepartmentCreate(BaseModel):
    name: str
    code: str
    hod_id: Optional[str] = None

class DepartmentResponse(BaseModel):
    id: str
    name: str
    code: str
    hod_id: Optional[str] = None
    hod_name: Optional[str] = None
    student_count: Optional[int] = 0
    mentor_count: Optional[int] = 0

# --- GEOFENCE SCHEMAS ---
class Coordinate(BaseModel):
    lat: float
    lng: float

class GeofenceZoneCreate(BaseModel):
    name: str
    department_id: str
    coordinates: List[Coordinate]  # Polygon coordinates
    center_lat: float
    center_lng: float
    radius_meters: float = 150.0

class GeofenceZoneResponse(BaseModel):
    id: str
    name: str
    department_id: str
    coordinates: List[Coordinate]
    center_lat: float
    center_lng: float
    radius_meters: float

# --- BIOMETRICS & ATTENDANCE SCHEMAS ---
class FaceEnrollmentRequest(BaseModel):
    student_id: str
    image_base64_list: List[str]  # 5-10 face photos

class AttendanceCheckinRequest(BaseModel):
    student_id: str
    lat: float
    lng: float
    face_image_base64: str  # Live camera frame
    wifi_ssid: Optional[str] = None
    wifi_bssid: Optional[str] = None
    liveness_challenge_response: Optional[str] = None
    liveness_score: Optional[float] = None

class OTPVerifyRequest(BaseModel):
    session_id: str
    otp_code: str

class AttendanceRecordResponse(BaseModel):
    id: str
    student_id: str
    student_name: Optional[str] = None
    department_id: Optional[str] = None
    date: str  # YYYY-MM-DD
    status: str  # "PRESENT", "ABSENT", "LATE", "LEAVE"
    confidence_score: float
    verification_method: str  # "BIOMETRIC_OTP", "BIOMETRIC_DIRECT", "MANUAL_CORRECTION", "FACULTY_SMART_PASS_SCAN"
    marked_at: datetime
    session_id: Optional[str] = None
    ledger_block_hash: Optional[str] = None
    ledger_block_height: Optional[int] = None
    wifi_verified: Optional[bool] = None
    liveness_score: Optional[float] = None

# --- CORRECTION & LEAVE SCHEMAS ---
class CorrectionRequestCreate(BaseModel):
    date: str  # YYYY-MM-DD
    reason: str
    claimed_time: str
    evidence_photo_base64: Optional[str] = None

class LeaveRequestCreate(BaseModel):
    reason: str
    from_date: str
    to_date: str
    document_url: Optional[str] = None

class ApprovalAction(BaseModel):
    request_id: str
    action: str  # "APPROVE", "REJECT", "ESCALATE"
    remark: Optional[str] = ""

# --- ML & PREDICTION SCHEMAS ---
class PredictionResponse(BaseModel):
    student_id: str
    student_name: Optional[str] = None
    department_id: Optional[str] = None
    risk_level: RiskLevel
    predicted_score: float  # e.g., 85.5% predicted academic performance
    attendance_pct: float
    exam_avg: float
    assignment_pct: float
    leave_count: int
    correction_count: int
    shap_top_features: List[Dict[str, Any]]
    generated_at: datetime

class MLThresholdConfig(BaseModel):
    low_risk_threshold: float = 75.0  # Above 75% -> Low risk
    high_risk_threshold: float = 60.0  # Below 60% -> High risk
    adaptive_otp_threshold: float = 0.85
    face_match_threshold: float = 0.60
