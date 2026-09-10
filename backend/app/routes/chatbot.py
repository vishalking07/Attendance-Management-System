from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.models.schemas import TokenData
from app.services.auth_service import get_current_user
from app.routes.users_data import mock_users_db, mock_performance_db, mock_attendance_db
from app.services.ml_service import get_model_metrics

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])

class ChatRequest(BaseModel):
    message: str
    student_id: Optional[str] = "usr_student_2"

class ChatResponse(BaseModel):
    reply: str
    intent: str
    suggestions: List[str]
    context_badges: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=ChatResponse)
async def query_academic_chatbot(
    payload: ChatRequest,
    current_user: TokenData = Depends(get_current_user)
):
    msg = payload.message.lower().strip()
    user_role = current_user.role
    user_id = current_user.user_id

    # Retrieve student context if applicable
    s_id = payload.student_id or user_id
    student_perf = mock_performance_db.get(s_id, {
        "attendance_pct": 64.0,
        "exam_avg": 54.0,
        "assignment_pct": 68.0,
        "leave_count": 4,
        "correction_count": 3
    })
    att_pct = student_perf.get("attendance_pct", 64.0)

    # Calculate Bunk Budget
    bunk_budget = max(0, int((att_pct - 75.0) / 1.5)) if att_pct > 75.0 else 0
    recovery_needed = max(0, int((75.0 - att_pct) / 0.8)) if att_pct < 75.0 else 0

    # 1. BUNK BUDGET & ATTENDANCE STATUS
    if any(k in msg for k in ["bunk", "leave", "safe miss", "cut off", "attendance", "percentage", "shortage"]):
        if att_pct >= 75.0:
            reply = (
                f"📊 **Attendance Health Check**:\n\n"
                f"Your current attendance is **{att_pct}%** (Above mandatory 75% cutoff).\n"
                f"• **Bunk Budget**: You can safely miss up to **{bunk_budget} classes** while remaining strictly compliant.\n"
                f"• **Velocity Status**: Stable. Keep attending lectures to maintain your academic momentum!"
            )
        else:
            reply = (
                f"⚠️ **Attendance Shortage Alert**:\n\n"
                f"Your current overall attendance is **{att_pct}%**, which is below the university 75.0% requirement.\n"
                f"• **Bunk Budget**: **0 classes**. Any further unexcused absence will trigger Tier-2 Mentor Escalation.\n"
                f"• **Recovery Goal**: You need to attend **{recovery_needed} consecutive classes** without absence to cross 75.0%.\n"
                f"• **Recommended Action**: Use the **'What-If' Prognosis Simulator** on your dashboard to model target score recovery, or submit a medical certificate under Leave Requests."
            )
        suggestions = ["Open 'What-If' Simulator", "How to file medical leave?", "Register Face Biometric"]
        intent = "ATTENDANCE_STATUS"

    # 2. BIOMETRIC REGISTRATION / ENROLLMENT
    elif any(k in msg for k in ["biometric", "face", "register", "enroll", "camera", "photo"]):
        reply = (
            f"📸 **Face Biometric Registration Workflow**:\n\n"
            f"1. On your Student Dashboard, click **'Register Face Biometric'** or open the Check-in page.\n"
            f"2. Look directly into the camera lens with good lighting.\n"
            f"3. The camera guides you through 3 captures: **Frontal, Left 15°, and Right 15°**.\n"
            f"4. The system extracts a normalized **128-dimensional biometric template vector** and logs an immutable cryptographic audit record.\n"
            f"5. Once enrolled, your daily check-in takes less than 2 seconds with active anti-spoofing defense!"
        )
        suggestions = ["What if my camera breaks?", "Check my attendance %", "What is Dynamic Smart Pass?"]
        intent = "BIOMETRIC_ENROLLMENT"

    # 3. SMART PASS & QR CODE / TOTP
    elif any(k in msg for k in ["smart pass", "qr", "totp", "code", "scanner", "faculty"]):
        reply = (
            f"🎫 **Dynamic Rotating TOTP Smart Pass**:\n\n"
            f"Your Smart Pass is a tamper-proof **Digital Student ID Card**:\n"
            f"• **Rotating 30-Second QR**: The QR code and 6-digit code update every 30 seconds with a cryptographic time-salt (prevents screenshot proxy scams).\n"
            f"• **Who Scans It?**: Your Faculty/Mentor scans it using the **Faculty Smart Pass Scanner** during class or exam hall entry.\n"
            f"• **Failover Backup**: If your selfie camera is broken or you don't have internet, present this pass to your teacher for 1-second bulk verification!"
        )
        suggestions = ["How does faculty scanner work?", "What is What-If Simulator?", "Check Bunk Budget"]
        intent = "SMART_PASS_EXPLANATION"

    # 4. WHAT-IF PROGNOSIS & ML SIMULATOR
    elif any(k in msg for k in ["what-if", "what if", "simulator", "prognosis", "prediction", "xgboost", "shap"]):
        reply = (
            f"🧠 **'What-If' Prescriptive Prognosis Engine**:\n\n"
            f"Powered by an **XGBoost Classifier with SHAP TreeExplainer**:\n"
            f"• Allows you to slide future attendance gains (+1 to +25 classes), projected internal test scores, and assignment submissions.\n"
            f"• Instantly calculates your new predicted score and forecasts risk level shifts (HIGH ➔ MEDIUM ➔ LOW).\n"
            f"• You can **'Commit Target Milestone'** to notify your mentor of your academic recovery contract!"
        )
        suggestions = ["Launch 'What-If' Modal", "Explain Bunk Budget", "View Peer Percentiles"]
        intent = "WHAT_IF_SIMULATOR"

    # 5. LEAVES & CORRECTIONS
    elif any(k in msg for k in ["leave", "medical", "duty", "correction", "request", "fever", "hospital"]):
        reply = (
            f"📝 **Academic Leave & Attendance Correction Portal**:\n\n"
            f"• **Medical / Duty Leaves**: Go to **Student ➔ Leave Requests**, select date range, reason, and attach a valid medical certificate or event invitation. Sent to Mentor & HOD for 2-tier digital approval.\n"
            f"• **Attendance Corrections**: If biometric check-in glitched or WiFi dropped at 09:00 AM, submit a timestamped dispute under **Correction Requests** within 48 hours."
        )
        suggestions = ["Check Leave Status", "Open Attendance Check-in", "My Bunk Budget"]
        intent = "LEAVE_CORRECTION_POLICY"

    # 6. DYNAMIC FACULTY 500M BEACON & PROXIMITY SHIELD
    elif any(k in msg for k in ["500m", "500", "proximity", "beacon", "faculty location", "distance", "in-class", "range"]):
        reply = (
            f"📡 **Dynamic Faculty Beacon (Strict 500m Proximity Shield)**:\n\n"
            f"Attendance is dynamically restricted strictly within **500 meters** of where your faculty is holding class:\n"
            f"• **Live Faculty Beacon**: Tracks the professor's live classroom beacon (e.g., CS-301, Lab, or live device GPS).\n"
            f"• **Strict Enforcement**: If you are within 500m (e.g., in class ~25m away), biometric & PIN check-ins succeed immediately.\n"
            f"• **Hostel/Proxy Block**: If you are outside 500m (e.g., at hostel ~780m away), check-in is rejected with a proximity violation alert.\n"
            f"• **Examiner Demo**: You can use the viva distance toggle on the Check-in page to demonstrate both in-range success and out-of-range rejection!"
        )
        suggestions = ["How does offline ID check-in work?", "Check session-wise attendance", "Open Check-in Radar"]
        intent = "FACULTY_500M_PROXIMITY"

    # 7. OFFLINE / NO-INTERNET ID CARD FALLBACK
    elif any(k in msg for k in ["offline", "no net", "no internet", "network drop", "data down", "id card", "physical id"]):
        reply = (
            f"🪪 **Offline / No-Internet Classroom ID Fallback**:\n\n"
            f"Never miss attendance because of mobile network issues or dead WiFi in class:\n"
            f"• **Zero Data Requirement**: If your phone runs out of battery or has no signal, simply show your physical College ID card to the professor.\n"
            f"• **Faculty 1-Click Verification**: The professor opens the **'Offline ID (No Net)'** tab on their Faculty Console, enters your Roll No (e.g., `21CS089`), and clicks **'Verify & Mark Present'**.\n"
            f"• **Audit Trail**: The system anchors an offline proxy-proof transaction into the immutable SHA-256 ledger with `OFFLINE_FACULTY_INSPECTED` status!"
        )
        suggestions = ["Check 500m Faculty Geofence", "View Today's Sessions", "Open Smart Pass"]
        intent = "OFFLINE_ID_FALLBACK"

    # 8. SESSION-WISE & DATE-WISE ATTENDANCE EXPLORER
    elif any(k in msg for k in ["session", "period", "timetable", "date wise", "date-wise", "calendar", "p1", "p2", "p3", "p4", "p5"]):
        reply = (
            f"📅 **Session-Wise & Date-Wise Attendance Explorer**:\n\n"
            f"Under **Student ➔ Attendance Calendar & Sessions**, you have granular full-day visibility:\n"
            f"• **Date Picker**: Choose any date (Today, Yesterday, or any historical date) using the date selector or 1-click quick chips.\n"
            f"• **5-Period Daily Timetable**: View Period 1 (08:45 AM) through Period 5 (04:15 PM) with real-time status (Present / Late / Absent / Scheduled).\n"
            f"• **Audit Telemetry**: Each session tile shows exact faculty distance (e.g., `24.5m / 500m`), verification method, and SHA-256 block hash!"
        )
        suggestions = ["Check 500m Faculty Beacon", "Bunk Budget Calculator", "How does Offline ID work?"]
        intent = "SESSION_WISE_ATTENDANCE"

    # 9. DUAL-SIGNAL GEOFENCE & SECURITY
    elif any(k in msg for k in ["geofence", "gps", "wifi", "bssid", "proxy"]):
        reply = (
            f"🛰️ **Dual-Signal Geofence & Campus Network Fusion**:\n\n"
            f"To prevent GPS spoofer apps and hostel-based attendance fraud:\n"
            f"• **Signal 1 (GPS Satellite)**: Checks if device is within the 200-meter campus polygon radius.\n"
            f"• **Signal 2 (Campus WiFi BSSID)**: Checks that the device is connected to the authorized EduNet campus mesh network.\n"
            f"• An **Isolation Forest unsupervised anomaly engine** flags impossible travel velocity and edge-of-fence clusters."
        )
        suggestions = ["What is 500m Faculty Proximity?", "What is Cryptographic Ledger?", "How to enroll Face ID?"]
        intent = "GEOFENCE_SECURITY"

    # 10. CRYPTOGRAPHIC LEDGER / BLOCKCHAIN
    elif any(k in msg for k in ["ledger", "blockchain", "hash", "sha-256", "block", "tamper"]):
        reply = (
            f"🔗 **Cryptographic Tamper-Proof Attendance Ledger**:\n\n"
            f"Every single check-in is cryptographically chained into an immutable SHA-256 ledger block:\n"
            f"• Each block records `Block Height`, `Student ID`, `Verification Method`, `Timestamp`, and `Previous Hash`.\n"
            f"• HODs and Admins can run a **1-Click Ledger Integrity Scan** to mathematically prove zero administrative tampering across all records."
        )
        suggestions = ["View Ledger Explorer", "Check ML Model Accuracy", "My Attendance Score"]
        intent = "LEDGER_EXPLANATION"

    # 8. GREETINGS & GENERAL HELP
    else:
        metrics = get_model_metrics()
        acc = metrics.get("accuracy", 94.2)
        reply = (
            f"👋 **Hello! I am your Bio-XAI Academic & Smart Attendance Assistant.**\n\n"
            f"I can help you navigate attendance rules, biometric registration, and academic recovery modeling.\n\n"
            f"**Quick Stats for You**:\n"
            f"• Your Attendance: **{att_pct}%**\n"
            f"• AI Model Accuracy: **{acc}% (XGBoost v2.4)**\n"
            f"• Bunk Budget: **{bunk_budget} safe misses**\n\n"
            f"How can I assist you today? Pick a quick topic below or type your question!"
        )
        suggestions = ["Check My Bunk Budget", "How to Register Face ID", "Explain 'What-If' Prognosis", "Why Smart Pass QR?"]
        intent = "GENERAL_GREETING"

    return ChatResponse(
        reply=reply,
        intent=intent,
        suggestions=suggestions,
        context_badges={
            "attendance_pct": att_pct,
            "bunk_budget": bunk_budget,
            "student_id": s_id
        }
    )
