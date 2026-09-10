# Shared data storage for runtime operation and seed fallback
mock_users_db = {}
mock_departments_db = {}
mock_geofence_db = {}
mock_embeddings_db = {}
mock_sessions_db = {
    "sess_live_default": {
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
        "started_at": "2026-09-10T09:00:00Z"
    }
}
mock_attendance_db = []
mock_corrections_db = []
mock_leaves_db = []
mock_performance_db = {}
mock_predictions_db = {}

