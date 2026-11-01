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

    # 1. 10 ACADEMIC DEPARTMENTS
    mock_departments_db.clear()
    depts_list = [
        ("dept_cs", "Computer Science & Engineering", "CS", "usr_hod_cs"),
        ("dept_ai_ds", "Artificial Intelligence & Data Science", "AI-DS", "usr_hod_aids"),
        ("dept_ece", "Electronics & Communication Engineering", "ECE", "usr_hod_ece"),
        ("dept_it", "Information Technology & Cloud Systems", "IT", "usr_hod_it"),
        ("dept_cyber", "Cybersecurity & Digital Forensics", "CYS", "usr_hod_cyber"),
        ("dept_robotics", "Robotics & Autonomous Automation", "RAI", "usr_hod_robotics"),
        ("dept_biomed", "Biomedical Engineering & Health Informatics", "BME", "usr_hod_biomed"),
        ("dept_mech", "Mechanical Engineering & Mechatronics", "MECH", "usr_hod_mech"),
        ("dept_aero", "Aerospace & Avionics Engineering", "AERO", "usr_hod_aero"),
        ("dept_civil", "Civil & Sustainable Infrastructure", "CIVIL", "usr_hod_civil")
    ]

    for d_id, name, code, h_id in depts_list:
        mock_departments_db[d_id] = {
            "id": d_id,
            "name": name,
            "code": code,
            "hod_id": h_id
        }

    # Default Passwords
    admin_pw = get_password_hash("Admin@123")
    hod_pw = get_password_hash("Hod@123")
    mentor_pw = get_password_hash("Mentor@123")
    student_pw = get_password_hash("Student@123")

    # Real non-animated person portrait photos (Unsplash high-resolution human portraits)
    REAL_STUDENT_PHOTOS = [
        "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=250&auto=format&fit=crop&q=80", # 1. Vishal (Young man)
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=250&auto=format&fit=crop&q=80", # 2. Nithishkumar (Young man)
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=250&auto=format&fit=crop&q=80", # 3. David Kumar
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=250&auto=format&fit=crop&q=80", # 4. Emily Chen
        "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=250&auto=format&fit=crop&q=80", # 5. Michael Scott
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=250&auto=format&fit=crop&q=80", # 6. Priya Sharma
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=250&auto=format&fit=crop&q=80", # 7. Rohan Patel
        "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=250&auto=format&fit=crop&q=80", # 8. Ananya Iyer
        "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=250&auto=format&fit=crop&q=80", # 9. Vikram Singh
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=250&auto=format&fit=crop&q=80", # 10. Kavya Nair
        "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=250&auto=format&fit=crop&q=80", # 11. Arjun Reddy
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=250&auto=format&fit=crop&q=80", # 12. Sneha Sen
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=250&auto=format&fit=crop&q=80", # 13. Karthik Raja
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=250&auto=format&fit=crop&q=80", # 14. Meera Krishnan
        "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=250&auto=format&fit=crop&q=80", # 15. Abhinav Gupta
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=250&auto=format&fit=crop&q=80", # 16. Divya Balan
        "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=250&auto=format&fit=crop&q=80", # 17. Sanjay Varma
        "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=250&auto=format&fit=crop&q=80", # 18. Keerthi Suresh
        "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=250&auto=format&fit=crop&q=80", # 19. Harish Kumar
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=250&auto=format&fit=crop&q=80", # 20. Shalini Menon
    ]

    REAL_FACULTY_PHOTOS = [
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1519741497674-611481863552?w=250&auto=format&fit=crop&q=80"
    ]

    REAL_MENTOR_PHOTOS = [
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=250&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=250&auto=format&fit=crop&q=80"
    ]

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
        "profile_photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=250&auto=format&fit=crop&q=80",
        "password_hash": admin_pw
    }

    # 10 HODs (One for each Department)
    hods_data = [
        ("usr_hod_cs", "Prof. Robert Langdon (HOD CS)", "hod.cs@bioxai.edu", "dept_cs"),
        ("usr_hod_aids", "Dr. Yoshua Bengio (HOD AI-DS)", "hod.aids@bioxai.edu", "dept_ai_ds"),
        ("usr_hod_ece", "Prof. Clara Oswald (HOD ECE)", "hod.ece@bioxai.edu", "dept_ece"),
        ("usr_hod_it", "Dr. Dennis Ritchie (HOD IT)", "hod.it@bioxai.edu", "dept_it"),
        ("usr_hod_cyber", "Dr. Kevin Mitnick (HOD Cyber)", "hod.cyber@bioxai.edu", "dept_cyber"),
        ("usr_hod_robotics", "Dr. Rodney Brooks (HOD Robotics)", "hod.robotics@bioxai.edu", "dept_robotics"),
        ("usr_hod_biomed", "Dr. Rosalind Franklin (HOD BioMed)", "hod.biomed@bioxai.edu", "dept_biomed"),
        ("usr_hod_mech", "Prof. James Watt (HOD Mech)", "hod.mech@bioxai.edu", "dept_mech"),
        ("usr_hod_aero", "Dr. A.P.J. Abdul Kalam (HOD Aero)", "hod.aero@bioxai.edu", "dept_aero"),
        ("usr_hod_civil", "Prof. M. Visvesvaraya (HOD Civil)", "hod.civil@bioxai.edu", "dept_civil")
    ]

    for idx, (h_id, name, email, d_id) in enumerate(hods_data):
        mock_users_db[email] = {
            "id": h_id,
            "name": name,
            "email": email,
            "phone": f"+1 555-01{len(mock_users_db):02d}",
            "role": "HOD",
            "department_id": d_id,
            "mentor_id": None,
            "profile_photo": REAL_FACULTY_PHOTOS[idx % len(REAL_FACULTY_PHOTOS)],
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
        "profile_photo": REAL_MENTOR_PHOTOS[0],
        "password_hash": mentor_pw
    }
    mock_users_db["mentor2.cs@bioxai.edu"] = {
        "id": "usr_mentor2",
        "name": "Dr. Grace Hopper (Faculty Advisor)",
        "email": "mentor2.cs@bioxai.edu",
        "phone": "+1 555-0104",
        "role": "MENTOR",
        "department_id": "dept_ai_ds",
        "mentor_id": None,
        "profile_photo": REAL_MENTOR_PHOTOS[1],
        "password_hash": mentor_pw
    }
    mock_users_db["mentor3.ece@bioxai.edu"] = {
        "id": "usr_mentor3",
        "name": "Dr. Nikola Tesla (Faculty Advisor)",
        "email": "mentor3.ece@bioxai.edu",
        "phone": "+1 555-0105",
        "role": "MENTOR",
        "department_id": "dept_ece",
        "mentor_id": None,
        "profile_photo": REAL_MENTOR_PHOTOS[2],
        "password_hash": mentor_pw
    }
    mock_users_db["mentor4.it@bioxai.edu"] = {
        "id": "usr_mentor4",
        "name": "Dr. Tim Berners-Lee (Faculty Advisor)",
        "email": "mentor4.it@bioxai.edu",
        "phone": "+1 555-0106",
        "role": "MENTOR",
        "department_id": "dept_it",
        "mentor_id": None,
        "profile_photo": REAL_MENTOR_PHOTOS[3],
        "password_hash": mentor_pw
    }
    mock_users_db["mentor5.mech@bioxai.edu"] = {
        "id": "usr_mentor5",
        "name": "Dr. Marie Curie (Faculty Advisor)",
        "email": "mentor5.mech@bioxai.edu",
        "phone": "+1 555-0107",
        "role": "MENTOR",
        "department_id": "dept_mech",
        "mentor_id": None,
        "profile_photo": REAL_MENTOR_PHOTOS[4],
        "password_hash": mentor_pw
    }

    # 20 Diverse Students with Vishal & Nithishkumar as Teammates
    students_data = [
        ("Vishal", "vishal@student.bioxai.edu", "dept_cs", "usr_mentor1", 93.5, 88.0, 95.0, 0, 0), # 1. Teammate 1 / Lead
        ("Nithishkumar", "nithishkumar@student.bioxai.edu", "dept_ai_ds", "usr_mentor2", 84.0, 78.0, 86.0, 1, 0), # 2. Teammate 2
        ("David Kumar", "david.kumar@student.bioxai.edu", "dept_ece", "usr_mentor3", 85.0, 78.0, 86.0, 1, 0), # 3.
        ("Emily Chen", "emily.chen@student.bioxai.edu", "dept_it", "usr_mentor4", 58.0, 48.0, 60.0, 5, 2), # 4. High Risk!
        ("Michael Scott", "michael.scott@student.bioxai.edu", "dept_mech", "usr_mentor5", 76.0, 72.0, 78.0, 2, 1), # 5.
        ("Priya Sharma", "priya.sharma@student.bioxai.edu", "dept_cyber", "usr_mentor1", 89.0, 84.0, 90.0, 1, 0), # 6.
        ("Rohan Patel", "rohan.patel@student.bioxai.edu", "dept_robotics", "usr_mentor3", 71.0, 66.0, 74.0, 3, 2), # 7. Shortage Warning!
        ("Ananya Iyer", "ananya.iyer@student.bioxai.edu", "dept_biomed", "usr_mentor5", 96.0, 92.0, 98.0, 0, 0), # 8. Star Performer
        ("Vikram Singh", "vikram.singh@student.bioxai.edu", "dept_aero", "usr_mentor5", 52.0, 45.0, 55.0, 6, 3), # 9. Severe Deficit
        ("Kavya Nair", "kavya.nair@student.bioxai.edu", "dept_civil", "usr_mentor2", 82.0, 80.0, 85.0, 1, 1), # 10.
        ("Arjun Reddy", "arjun.reddy@student.bioxai.edu", "dept_cs", "usr_mentor1", 91.0, 86.0, 92.0, 0, 0), # 11.
        ("Sneha Sen", "sneha.sen@student.bioxai.edu", "dept_ai_ds", "usr_mentor2", 73.5, 68.0, 72.0, 3, 1), # 12. Warning 73.5%
        ("Karthik Raja", "karthik.raja@student.bioxai.edu", "dept_ece", "usr_mentor3", 62.0, 54.0, 65.0, 4, 2), # 13. High Risk
        ("Meera Krishnan", "meera.krishnan@student.bioxai.edu", "dept_it", "usr_mentor4", 88.5, 82.0, 89.0, 1, 0), # 14.
        ("Abhinav Gupta", "abhinav.gupta@student.bioxai.edu", "dept_cyber", "usr_mentor1", 95.0, 91.0, 96.0, 0, 0), # 15. Honor Roll
        ("Divya Balan", "divya.balan@student.bioxai.edu", "dept_robotics", "usr_mentor3", 77.0, 74.0, 80.0, 2, 0), # 16.
        ("Sanjay Varma", "sanjay.varma@student.bioxai.edu", "dept_biomed", "usr_mentor5", 54.0, 46.0, 52.0, 5, 2), # 17. High Risk Deficit
        ("Keerthi Suresh", "keerthi.suresh@student.bioxai.edu", "dept_mech", "usr_mentor5", 83.0, 79.0, 85.0, 1, 1), # 18.
        ("Harish Kumar", "harish.kumar@student.bioxai.edu", "dept_aero", "usr_mentor5", 74.0, 70.0, 76.0, 2, 1), # 19. Borderline 74%
        ("Shalini Menon", "shalini.menon@student.bioxai.edu", "dept_civil", "usr_mentor2", 92.5, 89.0, 94.0, 0, 0) # 20. Consistent
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
            "profile_photo": REAL_STUDENT_PHOTOS[idx % len(REAL_STUDENT_PHOTOS)],
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

        # Seed 14 days of realistic past attendance history (yesterday backwards)
        today = datetime.now()
        for d in range(1, 15):
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

    # 3. 10 CAMPUS POLYGON GEOFENCE ZONES (One for each Department)
    mock_geofence_db.clear()
    geofences_data = [
        ("geo_cs", "Computer Science & Software Complex", "dept_cs", 12.9716, 77.5946, 200.0),
        ("geo_aids", "AI Innovation Hub & GPU Compute Center", "dept_ai_ds", 12.9725, 77.5955, 190.0),
        ("geo_ece", "Electronics & Silicon Nano-Lab Complex", "dept_ece", 12.9750, 77.5980, 180.0),
        ("geo_it", "Information Technology & Cloud Systems Wing", "dept_it", 12.9735, 77.5965, 185.0),
        ("geo_cyber", "Cyber Defense Operations Center", "dept_cyber", 12.9742, 77.5940, 175.0),
        ("geo_robotics", "Autonomous Mechatronics Arena & Drone Field", "dept_robotics", 12.9760, 77.5995, 210.0),
        ("geo_biomed", "Bio-Instrumentation & Genomic Informatics Lab", "dept_biomed", 12.9705, 77.5930, 170.0),
        ("geo_mech", "Mechanical Engineering & Thermal Research Hall", "dept_mech", 12.9690, 77.5920, 220.0),
        ("geo_aero", "Aerospace Propulsion & Wind Tunnel Facility", "dept_aero", 12.9775, 77.6010, 250.0),
        ("geo_civil", "Sustainable Smart Cities & Geomatics Complex", "dept_civil", 12.9680, 77.5910, 200.0)
    ]

    for g_id, name, d_id, lat, lng, radius in geofences_data:
        mock_geofence_db[g_id] = {
            "id": g_id,
            "name": name,
            "department_id": d_id,
            "center_lat": lat,
            "center_lng": lng,
            "radius_meters": radius,
            "coordinates": [
                {"lat": round(lat + 0.0010, 4), "lng": round(lng - 0.0010, 4)},
                {"lat": round(lat + 0.0010, 4), "lng": round(lng + 0.0010, 4)},
                {"lat": round(lat - 0.0010, 4), "lng": round(lng + 0.0010, 4)},
                {"lat": round(lat - 0.0010, 4), "lng": round(lng - 0.0010, 4)}
            ]
        }

    # 4. SAMPLE LEAVE REQUESTS (Pending, Approved, Rejected)
    mock_leaves_db.clear()
    mock_leaves_db.extend([
        {
            "id": "leave_1",
            "student_id": "usr_student_1",
            "student_name": "Vishal",
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
            "student_id": "usr_student_2",
            "student_name": "Nithishkumar",
            "department_id": "dept_ai_ds",
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
            "student_id": "usr_student_1",
            "student_name": "Vishal",
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

