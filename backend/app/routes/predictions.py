from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from app.models.schemas import PredictionResponse, RiskLevel, UserRole, TokenData
from app.services.auth_service import get_current_user
from app.services.ml_service import predict_student_risk
from app.routes.users_data import mock_users_db, mock_performance_db, mock_predictions_db, mock_attendance_db

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get("", response_model=List[PredictionResponse])
async def get_predictions(
    student_id: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user)
):
    students = [u for u in mock_users_db.values() if u["role"] == UserRole.STUDENT]

    # Data Scoping
    if current_user.role == UserRole.STUDENT:
        students = [u for u in students if u["id"] == current_user.user_id]
    elif current_user.role == UserRole.MENTOR:
        students = [u for u in students if u.get("mentor_id") == current_user.user_id or u["id"] == student_id]
    elif current_user.role == UserRole.HOD:
        students = [u for u in students if u.get("department_id") == current_user.department_id]

    if student_id and current_user.role != UserRole.STUDENT:
        students = [u for u in students if u["id"] == student_id]

    results = []
    for s in students:
        s_id = s["id"]
        
        # Calculate real-time attendance %
        s_att_records = [a for a in mock_attendance_db if a["student_id"] == s_id]
        if s_att_records:
            present_count = len([a for a in s_att_records if a["status"] == "PRESENT"])
            att_pct = round((present_count / len(s_att_records)) * 100, 1)
        else:
            att_pct = 78.5  # Seed default

        # Fetch performance features
        perf = mock_performance_db.get(s_id, {
            "attendance_pct": att_pct,
            "exam_avg": 72.0,
            "assignment_pct": 82.0,
            "leave_count": 1,
            "correction_count": 0
        })
        perf["attendance_pct"] = att_pct

        # Predict Risk + SHAP feature contributions
        risk_level, predicted_score, shap_features = predict_student_risk(perf)

        results.append({
            "student_id": s_id,
            "student_name": s["name"],
            "department_id": s.get("department_id"),
            "risk_level": risk_level,
            "predicted_score": predicted_score,
            "attendance_pct": att_pct,
            "exam_avg": perf.get("exam_avg", 70.0),
            "assignment_pct": perf.get("assignment_pct", 80.0),
            "leave_count": perf.get("leave_count", 0),
            "correction_count": perf.get("correction_count", 0),
            "shap_top_features": shap_features,
            "generated_at": datetime.utcnow()
        })

    return results
