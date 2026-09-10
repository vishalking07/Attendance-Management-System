from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from app.models.schemas import MLThresholdConfig, UserRole, TokenData
from app.services.auth_service import require_roles
from app.services.ml_service import train_risk_prediction_model, ml_manager, get_model_metrics
from app.services.notification_service import in_memory_audit_logs, log_audit_event
from app.config import settings
from app.routes.users_data import mock_users_db, mock_departments_db, mock_attendance_db

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/analytics")
async def get_system_analytics(current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))):
    total_students = len([u for u in mock_users_db.values() if u["role"] == UserRole.STUDENT])
    total_mentors = len([u for u in mock_users_db.values() if u["role"] == UserRole.MENTOR])
    total_hods = len([u for u in mock_users_db.values() if u["role"] == UserRole.HOD])

    # Institution overall attendance %
    if mock_attendance_db:
        p_count = len([a for a in mock_attendance_db if a["status"] == "PRESENT"])
        overall_att_pct = round((p_count / len(mock_attendance_db)) * 100, 1)
    else:
        overall_att_pct = 84.2

    # Department comparisons
    dept_stats = []
    for d_id, dept in mock_departments_db.items():
        d_students = [u["id"] for u in mock_users_db.values() if u["role"] == UserRole.STUDENT and u.get("department_id") == d_id]
        d_att = [a for a in mock_attendance_db if a.get("department_id") == d_id]
        att_pct = round((len([a for a in d_att if a["status"] == "PRESENT"]) / max(1, len(d_att))) * 100, 1) if d_att else 82.0
        dept_stats.append({
            "department_id": d_id,
            "department_name": dept["name"],
            "student_count": len(d_students),
            "attendance_pct": att_pct
        })

    return {
        "total_students": total_students,
        "total_mentors": total_mentors,
        "total_hods": total_hods,
        "total_departments": len(mock_departments_db),
        "overall_attendance_pct": overall_att_pct,
        "at_risk_students_count": 3,
        "department_stats": dept_stats
    }

@router.post("/retrain-model")
async def retrain_ml_model(current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))):
    result = train_risk_prediction_model()
    await log_audit_event(
        actor_id=current_user.user_id,
        actor_name=current_user.role,
        action="RETRAIN_ML_MODEL",
        target="XGBoost Classifier",
        details=f"Retrained student risk prediction model. Accuracy achieved: {result['accuracy']*100:.2f}%"
    )
    return {"status": "success", "message": f"ML Model Retrained Successfully. Test Accuracy: {result['accuracy']*100:.2f}%", "metrics": result.get("metrics")}

@router.get("/ml-metrics")
async def get_ml_metrics_endpoint(current_user: TokenData = Depends(require_roles([UserRole.ADMIN, UserRole.HOD]))):
    return get_model_metrics()

@router.get("/audit-logs")
async def get_audit_logs(current_user: TokenData = Depends(require_roles([UserRole.ADMIN]))):
    return in_memory_audit_logs[:50]
