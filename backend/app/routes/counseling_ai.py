from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.schemas import UserRole, TokenData
from app.services.auth_service import get_current_user
from app.services.ml_service import predict_student_risk
from app.services.notification_service import create_notification, log_audit_event
from app.routes.users_data import mock_users_db, mock_performance_db, mock_attendance_db

router = APIRouter(prefix="/counseling", tags=["AI Counseling & Intervention"])

# In-memory dossiers store
mock_dossiers_db: List[Dict[str, Any]] = [
    {
        "id": "dossier_001",
        "student_id": "usr_stu_002",
        "student_name": "Marcus Vance",
        "department_id": "dept_cs",
        "mentor_id": "usr_men_001",
        "mentor_name": "Dr. Alan Turing",
        "risk_level": "HIGH",
        "generated_at": "2026-09-08T14:30:00Z",
        "hod_endorsed": True,
        "hod_endorsed_by": "Dr. Katherine Johnson",
        "hod_remarks": "Approved for faculty remedial clinic and bi-weekly attendance check.",
        "attendance_pct": 58.4,
        "predicted_score": 52.0,
        "swot": {
            "strengths": ["Strong lab assignment scores (85%)", "Good problem-solving in practical sessions"],
            "weaknesses": ["Severe morning lecture absenteeism (58.4% attendance)", "Missed Internal Test 1"],
            "opportunities": ["Available remedial tutorial batch starting next Monday", "Peer-mentoring pairing with high-attendance study group"],
            "threats": ["Risk of university debarment if attendance does not reach 75% within 18 days"]
        },
        "talking_points": [
            "Inquire about specific challenges with the 8:30 AM Data Structures lecture.",
            "Review makeup assignments for missed Internal Test 1.",
            "Establish a firm daily check-in commitment with peer study partner."
        ],
        "action_plan": [
            {"week": "Week 1", "action": "Attend all 5 scheduled core lectures; clear zero absences.", "status": "COMPLETED"},
            {"week": "Week 2", "action": "Submit revised Algorithm complexity assignment for grade recovery.", "status": "IN_PROGRESS"},
            {"week": "Week 3", "action": "Take Mid-Term makeup assessment and achieve >= 70%.", "status": "PENDING"}
        ]
    }
]

class GenerateDossierRequest(BaseModel):
    student_id: str
    custom_notes: Optional[str] = None

class HODEndorsementRequest(BaseModel):
    dossier_id: str
    remarks: str
    escalate_to_dean: bool = False

@router.post("/generate-dossier")
async def generate_counseling_dossier(
    payload: GenerateDossierRequest,
    current_user: TokenData = Depends(get_current_user)
):
    student = next((u for u in mock_users_db.values() if u["id"] == payload.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    s_id = student["id"]
    s_records = [a for a in mock_attendance_db if a["student_id"] == s_id]
    total_conducted = max(len(s_records), 20)
    present_count = len([a for a in s_records if a["status"] == "PRESENT"]) if s_records else 14
    att_pct = round((present_count / total_conducted) * 100, 1)

    perf = mock_performance_db.get(s_id, {
        "attendance_pct": att_pct,
        "exam_avg": 64.0,
        "assignment_pct": 74.0,
        "leave_count": 2,
        "correction_count": 1
    })

    risk_level, predicted_score, shap_features = predict_student_risk(perf)

    # Auto-generate dynamic SWOT & Action items based on SHAP deficit
    top_negative_factors = [f["description"] for f in shap_features if f["impact"] == "NEGATIVE"]
    
    strengths = [
        f"Consistently high assignment completion ({perf.get('assignment_pct', 75)}%)",
        "Active participation in campus lab sessions",
        "Clean biometric integrity verification record"
    ]
    weaknesses = [
        f"Attendance standing at {att_pct}% (below mandatory 75% cutoff)",
        f"Primary risk driver: {top_negative_factors[0] if top_negative_factors else 'Recent absence streak'}",
        "Vulnerability to cumulative credit loss"
    ]
    opportunities = [
        "Eligibility for faculty-led accelerated makeup sessions",
        "Pairing with academic department honor mentor",
        "Self-paced learning module completion credits"
    ]
    threats = [
        "Risk of examination hall debarment if absent for 3 more sessions",
        "GPA suppression below degree placement eligibility cutoff"
    ]

    talking_points = [
        f"Directly discuss root causes behind {att_pct}% attendance and identify transportation or health constraints.",
        f"Review recent performance in exams (average {perf.get('exam_avg', 65)}%) and schedule faculty office hours.",
        "Align on the Minimum Effort Attendance Target to ensure 75% clearance before semester closure."
    ]

    action_plan = [
        {"week": "Week 1", "action": f"Achieve 100% attendance in upcoming 5 lecture blocks without unexcused absence.", "status": "PENDING"},
        {"week": "Week 2", "action": "Attend remedial lab session and submit practice problem sets.", "status": "PENDING"},
        {"week": "Week 3", "action": "Complete mentor progress review meeting and re-evaluate XAI risk score.", "status": "PENDING"}
    ]

    dossier_id = f"dossier_{len(mock_dossiers_db) + 1:03d}"
    dossier = {
        "id": dossier_id,
        "student_id": s_id,
        "student_name": student["name"],
        "department_id": student.get("department_id", "dept_cs"),
        "mentor_id": student.get("mentor_id", current_user.user_id),
        "mentor_name": current_user.role,
        "risk_level": risk_level.value,
        "generated_at": datetime.utcnow().isoformat(),
        "hod_endorsed": False,
        "hod_endorsed_by": None,
        "hod_remarks": None,
        "attendance_pct": att_pct,
        "predicted_score": predicted_score,
        "swot": {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats
        },
        "talking_points": talking_points,
        "action_plan": action_plan,
        "custom_notes": payload.custom_notes
    }

    mock_dossiers_db.append(dossier)

    # Notify student about academic recovery plan
    await create_notification(
        user_id=s_id,
        title="✨ Personalized AI Recovery Plan Generated",
        message=f"Your mentor created an AI Intervention Dossier with tailored goals to restore your attendance to {att_pct + 12}%.",
        notification_type="INFO"
    )

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="AI_COUNSELING_DOSSIER_GENERATED",
        target=s_id,
        details=f"Generated dossier {dossier_id} for {student['name']}. Risk Tier: {risk_level.value}"
    )

    return dossier

@router.post("/hod-endorse")
async def endorse_counseling_dossier(
    payload: HODEndorsementRequest,
    current_user: TokenData = Depends(get_current_user)
):
    dossier = next((d for d in mock_dossiers_db if d["id"] == payload.dossier_id), None)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier record not found")

    dossier["hod_endorsed"] = True
    dossier["hod_endorsed_by"] = current_user.role
    dossier["hod_remarks"] = payload.remarks
    dossier["escalated_to_dean"] = payload.escalate_to_dean
    dossier["endorsed_at"] = datetime.utcnow().isoformat()

    # Notify student and mentor
    await create_notification(
        user_id=dossier["student_id"],
        title="Department Head Endorsed Intervention",
        message=f"HOD approved your academic recovery dossier: '{payload.remarks}'",
        notification_type="SUCCESS"
    )

    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="HOD_DOSSIER_ENDORSEMENT",
        target=payload.dossier_id,
        details=f"HOD endorsed dossier {payload.dossier_id} with remarks: {payload.remarks}"
    )

    return {
        "status": "ENDORSED",
        "message": "Counseling dossier signed and endorsed by HOD successfully.",
        "dossier": dossier
    }

@router.get("/list")
async def get_counseling_dossiers(
    student_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    dossiers = list(mock_dossiers_db)
    if current_user.role == UserRole.STUDENT:
        dossiers = [d for d in dossiers if d["student_id"] == current_user.user_id]
    elif student_id:
        dossiers = [d for d in dossiers if d["student_id"] == student_id]
    return dossiers
