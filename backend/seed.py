import logging
import random
from datetime import datetime, timedelta
from app.services.auth_service import get_password_hash
from app.routes.users_data import (
    mock_users_db, mock_departments_db, mock_geofence_db,
    mock_attendance_db, mock_performance_db, mock_corrections_db, mock_leaves_db,
    mock_embeddings_db
)
from app.services.ledger_service import create_attendance_block

logger = logging.getLogger(__name__)

def seed_database_data():
    logger.info("🌱 Seeding Database with 10 student accounts, departments, polygon geofences, and synthetic metrics...")

    # 1. DEPARTMENTS
    mock_departments_db["dept_cs"] = {
        "id": "dept_cs",
        "name": "Computer Science & AI",
        "code": "CS",
        "hod_id": "usr_hod_cs"
    }
    mock_departments_db["dept_ece"] = {
        "id": "dept_ece",
        "name": "Electronics & Communication",
        "code": "ECE",
        "hod_id": "usr_hod_ece"
    }

    # Default Passwords
    admin_pw = get_password_hash("Admin@123")
    hod_pw = get_password_hash("Hod@123")
    mentor_pw = get_password_hash("Mentor@123")
    student_pw = get_password_hash("Student@123")

    # 2. USERS
    # Admin
    mock_users_db["admin@bioxai.edu"] = {
        "id": "usr_admin",
        "name": "Dr. Eleanor Vance (System Admin)",
        "email": "admin@bioxai.edu",
        "phone": "+1 555-0100",
        "role": "ADMIN",
        "department_id": None,
        "mentor_id": None,
        "profile_photo": "https://api.dicebear.com/7.x/avataaars/svg?seed=Eleanor",
        "password_hash": admin_pw
    }

    # HODs
    mock_users_db["hod.cs@bioxai.edu"] = {
        "id": "usr_hod_cs",
        "name": "Prof. Robert Langdon (HOD CS)",
        "email": "hod.cs@bioxai.edu",
        "phone": "+1 555-0101",
        "role": "HOD",
        "department_id": "dept_cs",
        "mentor_id": None,
        "profile_photo": "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert",
        "password_hash": hod_pw
    }
    mock_users_db["hod.ece@bioxai.edu"] = {
        "id": "usr_hod_ece",
        "name": "Prof. Clara Oswald (HOD ECE)",
        "email": "hod.ece@bioxai.edu",
        "phone": "+1 555-0102",
        "role": "HOD",
        "department_id": "dept_ece",
        "mentor_id": None,
        "profile_photo": "https://api.dicebear.com/7.x/avataaars/svg?seed=Clara",
        "password_hash": hod_pw
    }

    # Mentors
    mock_users_db["mentor1.cs@bioxai.edu"] = {
        "id": "usr_mentor1",
        "name": "Dr. Alan Turing (Faculty Advisor)",
        "email": "mentor1.cs@bioxai.edu",
        "phone": "+1 555-0103",
        "role": "MENTOR",
        "department_id": "dept_cs",
        "mentor_id": None,
        "profile_photo": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alan",
        "password_hash": mentor_pw
    }
    mock_users_db["mentor2.cs@bioxai.edu"] = {
        "id": "usr_mentor2",
        "name": "Dr. Grace Hopper (Faculty Advisor)",
        "email": "mentor2.cs@bioxai.edu",
        "phone": "+1 555-0104",
        "role": "MENTOR",
        "department_id": "dept_cs",
        "mentor_id": None,
        "profile_photo": "https://api.dicebear.com/7.x/avataaars/svg?seed=Grace",
        "password_hash": mentor_pw
    }

    # 10 Diverse Students across CS and ECE
    students_data = [
        ("Alex Smith", "alex.smith@student.bioxai.edu", "dept_cs", "usr_mentor1", 93.5, 88.0, 95.0, 0, 0),
        ("Sarah Jenkins", "sarah.jenkins@student.bioxai.edu", "dept_cs", "usr_mentor1", 64.0, 54.0, 68.0, 4, 3), # At Risk!
        ("David Kumar", "david.kumar@student.bioxai.edu", "dept_cs", "usr_mentor2", 85.0, 78.0, 86.0, 1, 0),
        ("Emily Chen", "emily.chen@student.bioxai.edu", "dept_cs", "usr_mentor2", 58.0, 48.0, 60.0, 5, 2), # High Risk!
        ("Michael Scott", "michael.scott@student.bioxai.edu", "dept_ece", "usr_mentor1", 76.0, 72.0, 78.0, 2, 1),
        ("Priya Sharma", "priya.sharma@student.bioxai.edu", "dept_cs", "usr_mentor1", 89.0, 84.0, 90.0, 1, 0),
        ("Rohan Patel", "rohan.patel@student.bioxai.edu", "dept_cs", "usr_mentor2", 71.0, 66.0, 74.0, 3, 2), # Shortage Warning!
        ("Ananya Iyer", "ananya.iyer@student.bioxai.edu", "dept_ece", "usr_mentor2", 96.0, 92.0, 98.0, 0, 0), # Star Performer
        ("Vikram Singh", "vikram.singh@student.bioxai.edu", "dept_ece", "usr_mentor1", 52.0, 45.0, 55.0, 6, 3), # Severe Deficit
        ("Kavya Nair", "kavya.nair@student.bioxai.edu", "dept_cs", "usr_mentor2", 82.0, 80.0, 85.0, 1, 1)
    ]

    for idx, (name, email, d_id, m_id, att, ex, asg, l_cnt, c_cnt) in enumerate(students_data):
        s_id = f"usr_student_{idx+1}"
        mock_users_db[email] = {
            "id": s_id,
            "name": name,
            "email": email,
            "phone": f"+1 555-02{idx:02d}",
            "role": "STUDENT",
            "department_id": d_id,
            "mentor_id": m_id,
            "profile_photo": f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}",
            "password_hash": student_pw
        }
        
        # Performance metrics
        mock_performance_db[s_id] = {
            "student_id": s_id,
            "attendance_pct": att,
            "exam_avg": ex,
            "assignment_pct": asg,
            "leave_count": l_cnt,
            "correction_count": c_cnt
        }

        # Seed baseline 128-d face embedding template
        random.seed(idx + 42)
        base_vector = [round(random.gauss(0.0, 0.2), 4) for _ in range(128)]
        norm = sum(x**2 for x in base_vector) ** 0.5
        mock_embeddings_db[s_id] = {
            "student_id": s_id,
            "embedding_vector": [round(x / norm, 4) for x in base_vector],
            "created_at": datetime.utcnow().isoformat()
        }

        # Seed 14 days of realistic attendance history
        today = datetime.now()
        for d in range(14):
            past_date = (today - timedelta(days=d)).strftime("%Y-%m-%d")
            # Determine status based on student attendance rate
            if att < 60:
                status = "PRESENT" if (d % 3 == 0) else "ABSENT"
            elif att < 75:
                status = "ABSENT" if (d in [2, 5, 9, 12]) else "PRESENT"
            else:
                status = "PRESENT" if (d != 6) else "ABSENT"

            rec_id = f"att_seed_{s_id}_{d}"
            rec = {
                "id": rec_id,
                "student_id": s_id,
                "student_name": name,
                "department_id": d_id,
                "date": past_date,
                "status": status,
                "confidence_score": round(0.92 + (idx * 0.005), 2) if status == "PRESENT" else 0.0,
                "verification_method": "BIOMETRIC_DIRECT" if status == "PRESENT" else "AUTO_ABSENCE",
                "marked_at": f"{past_date}T09:{10 + (d % 15):02d}:00"
            }
            mock_attendance_db.append(rec)

            # Pre-seed initial 10 blocks into cryptographic ledger chain
            if idx == 1 and d < 10 and status == "PRESENT":
                try:
                    create_attendance_block(rec)
                except Exception:
                    pass

    # 3. POLYGON GEOFENCE ZONES
    mock_geofence_db["geo_cs"] = {
        "id": "geo_cs",
        "name": "Computer Science Building & Campus Center",
        "department_id": "dept_cs",
        "center_lat": 12.9716,
        "center_lng": 77.5946,
        "radius_meters": 200.0,
        "coordinates": [
            {"lat": 12.9725, "lng": 77.5935},
            {"lat": 12.9725, "lng": 77.5957},
            {"lat": 12.9705, "lng": 77.5957},
            {"lat": 12.9705, "lng": 77.5935}
        ]
    }
    mock_geofence_db["geo_ece"] = {
        "id": "geo_ece",
        "name": "Electronics & Embedded Systems Complex",
        "department_id": "dept_ece",
        "center_lat": 12.9750,
        "center_lng": 77.5980,
        "radius_meters": 180.0,
        "coordinates": [
            {"lat": 12.9760, "lng": 77.5970},
            {"lat": 12.9760, "lng": 77.5990},
            {"lat": 12.9740, "lng": 77.5990},
            {"lat": 12.9740, "lng": 77.5970}
        ]
    }

    # 4. SAMPLE LEAVE REQUESTS (Pending, Approved, Rejected)
    mock_leaves_db.clear()
    mock_leaves_db.extend([
        {
            "id": "leave_1",
            "student_id": "usr_student_2",
            "student_name": "Sarah Jenkins",
            "department_id": "dept_cs",
            "reason": "Viral fever and acute migraine symptoms",
            "from_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "to_date": datetime.now().strftime("%Y-%m-%d"),
            "document_url": "https://example.com/medical_certificate.pdf",
            "status": "PENDING",
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "approval_trail": []
        },
        {
            "id": "leave_2",
            "student_id": "usr_student_7",
            "student_name": "Rohan Patel",
            "department_id": "dept_cs",
            "reason": "Inter-Collegiate Hackathon & Robotics Championship",
            "from_date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "to_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "document_url": "https://example.com/hackathon_invite.pdf",
            "status": "APPROVED",
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "approval_trail": [{"actor": "Dr. Grace Hopper", "action": "APPROVED", "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat()}]
        },
        {
            "id": "leave_3",
            "student_id": "usr_student_9",
            "student_name": "Vikram Singh",
            "department_id": "dept_ece",
            "reason": "Personal travel without prior department intimation",
            "from_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "to_date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
            "document_url": None,
            "status": "REJECTED",
            "created_at": (datetime.utcnow() - timedelta(days=8)).isoformat(),
            "approval_trail": [{"actor": "Dr. Alan Turing", "action": "REJECTED", "timestamp": (datetime.utcnow() - timedelta(days=7)).isoformat()}]
        },
        {
            "id": "leave_4",
            "student_id": "usr_student_4",
            "student_name": "Emily Chen",
            "department_id": "dept_cs",
            "reason": "Family emergency and clinical hospitalization assistance",
            "from_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "to_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "document_url": "https://example.com/hospital_intimation.pdf",
            "status": "PENDING",
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "approval_trail": []
        }
    ])

    # 5. SAMPLE ATTENDANCE CORRECTIONS
    mock_corrections_db.clear()
    mock_corrections_db.extend([
        {
            "id": "corr_1",
            "student_id": "usr_student_2",
            "student_name": "Sarah Jenkins",
            "department_id": "dept_cs",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "reason": "Webcam liveness check glitched due to low lighting in seminar room 302",
            "claimed_time": "09:12 AM",
            "evidence_photo_base64": None,
            "status": "PENDING",
            "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "approval_trail": []
        },
        {
            "id": "corr_2",
            "student_id": "usr_student_3",
            "student_name": "David Kumar",
            "department_id": "dept_cs",
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "reason": "Campus WiFi reconnect packet drop during 09:00 AM check-in surge",
            "claimed_time": "09:05 AM",
            "evidence_photo_base64": None,
            "status": "APPROVED",
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "approval_trail": [{"actor": "Dr. Alan Turing", "action": "APPROVED", "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat()}]
        },
        {
            "id": "corr_3",
            "student_id": "usr_student_4",
            "student_name": "Emily Chen",
            "department_id": "dept_cs",
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "reason": "Device battery shutdown right at OTP verification confirmation step",
            "claimed_time": "09:18 AM",
            "evidence_photo_base64": None,
            "status": "PENDING",
            "created_at": (datetime.utcnow() - timedelta(days=4)).isoformat(),
            "approval_trail": []
        }
    ])

    logger.info("✅ Database successfully seeded with 10 student profiles, 14-day history, ledger blocks, and embeddings.")

if __name__ == "__main__":
    seed_database_data()

