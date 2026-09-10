from datetime import datetime
from typing import Dict, Any, List
import random
import logging

logger = logging.getLogger(__name__)

def evaluate_attendance_anomaly(
    student_id: str,
    lat: float,
    lng: float,
    distance_to_center_m: float,
    geofence_radius_m: float,
    device_fingerprint: str = "BROWSER_CLIENT",
    ip_address: str = "127.0.0.1"
) -> Dict[str, Any]:
    """
    Evaluates proxy and outlier risk using heuristic spatial-temporal scoring
    and anomaly detection metrics.
    """
    flags = []
    anomaly_score = 0.05  # Base healthy baseline (5%)

    # 1. Edge-of-geofence anomaly (check-in at outer perimeter edge)
    perimeter_ratio = distance_to_center_m / max(geofence_radius_m, 1.0)
    if perimeter_ratio > 0.90:
        anomaly_score += 0.35
        flags.append({
            "type": "PERIMETER_PROXIMITY_ANOMALY",
            "severity": "MEDIUM",
            "detail": f"Check-in at outer edge boundary ({perimeter_ratio*100:.1f}% of allowable radius)."
        })
    elif perimeter_ratio > 0.80:
        anomaly_score += 0.15
        flags.append({
            "type": "NEAR_PERIMETER_WARNING",
            "severity": "LOW",
            "detail": f"Check-in within outer 20% boundary."
        })

    # 2. Time-of-day check (normal lecture slots are between 08:00 and 18:00)
    current_hour = datetime.now().hour
    if current_hour < 7 or current_hour > 19:
        anomaly_score += 0.30
        flags.append({
            "type": "OFF_HOURS_TIMESTAMP",
            "severity": "HIGH",
            "detail": f"Check-in logged outside academic operating hours ({current_hour}:00)."
        })

    # Clamp score between 0.0 and 1.0
    proxy_risk_pct = round(min(anomaly_score, 0.98) * 100, 1)

    # Classification
    if proxy_risk_pct >= 60:
        classification = "SUSPICIOUS_PROXY"
        threat_level = "HIGH"
    elif proxy_risk_pct >= 30:
        classification = "BORDERLINE_IRREGULAR"
        threat_level = "MEDIUM"
    else:
        classification = "CLEAN_AUTHENTIC"
        threat_level = "LOW"

    return {
        "student_id": student_id,
        "proxy_risk_pct": proxy_risk_pct,
        "classification": classification,
        "threat_level": threat_level,
        "flags": flags,
        "evaluated_at": datetime.utcnow().isoformat()
    }

def get_department_anomaly_queue() -> List[Dict[str, Any]]:
    """
    Returns mock active flagged anomalies for Mentor & HOD review.
    """
    return [
        {
            "id": "anom_101",
            "student_id": "usr_stu_002",
            "student_name": "Marcus Vance",
            "department_id": "dept_cs",
            "timestamp": datetime.now().strftime("%Y-%m-%d 08:58:12"),
            "proxy_risk_pct": 74.5,
            "threat_level": "HIGH",
            "primary_flag": "PERIMETER_PROXIMITY_ANOMALY",
            "details": "Check-in at 492m of 500m geofence perimeter with rapid device user-agent switch.",
            "status": "PENDING_REVIEW"
        },
        {
            "id": "anom_102",
            "student_id": "usr_stu_003",
            "student_name": "Elena Rostova",
            "department_id": "dept_cs",
            "timestamp": datetime.now().strftime("%Y-%m-%d 09:02:44"),
            "proxy_risk_pct": 42.0,
            "threat_level": "MEDIUM",
            "primary_flag": "NEAR_PERIMETER_WARNING",
            "details": "GPS jitter detected on mobile client connection.",
            "status": "REVIEWED"
        }
    ]
