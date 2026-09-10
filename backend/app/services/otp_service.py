import random
import hashlib
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# In-memory session OTP store (for fast single-use lookup)
# Structure: { session_id: { "otp_hash": str, "expires_at": datetime, "used": bool, "attempts": int, "otp_code_preview": str } }
otp_store: Dict[str, dict] = {}

def generate_otp() -> str:
    """Generates a 6-digit numeric OTP."""
    return f"{random.randint(100000, 999999)}"

def hash_otp(otp_code: str) -> str:
    return hashlib.sha256(otp_code.encode()).hexdigest()

def create_otp_session(session_id: str, student_email: str) -> Tuple[str, datetime]:
    """
    Creates a new single-use OTP for the attendance session.
    Returns: (otp_code_preview, expires_at)
    """
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(seconds=settings.OTP_VALIDITY_SECONDS)
    
    otp_store[session_id] = {
        "otp_hash": hash_otp(otp_code),
        "expires_at": expires_at,
        "used": False,
        "attempts": 0,
        "otp_code_preview": otp_code  # Retained in memory for dev/demo preview in UI/Console
    }

    logger.info(f"🔑 [DEMO OTP] Session {session_id} generated OTP: {otp_code} for {student_email} (Expires in {settings.OTP_VALIDITY_SECONDS}s)")
    
    # Try sending via SMTP if credentials configured
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            send_email_otp(student_email, otp_code)
        except Exception as e:
            logger.warning(f"Could not send OTP email via SMTP: {e}. Available via in-app notification.")

    return otp_code, expires_at

def verify_otp_code(session_id: str, otp_code_input: str) -> Tuple[bool, str]:
    """
    Validates entered OTP code.
    Enforces: correct code, not expired, not already used, max 3 attempts.
    """
    session = otp_store.get(session_id)
    if not session:
        return False, "Invalid or expired attendance session."

    if session["used"]:
        return False, "This OTP has already been used."

    if datetime.utcnow() > session["expires_at"]:
        return False, "OTP has expired. Please re-check in."

    session["attempts"] += 1
    if session["attempts"] > 3:
        session["used"] = True
        return False, "Too many failed attempts. Session invalidated."

    input_hash = hash_otp(otp_code_input)
    if input_hash == session["otp_hash"]:
        session["used"] = True
        return True, "OTP verified successfully."
    else:
        return False, f"Incorrect OTP. {3 - session['attempts']} attempts remaining."

def send_email_otp(recipient_email: str, otp_code: str):
    msg = MIMEText(f"Your Smart Attendance 2FA Verification Code is: {otp_code}\n\nValid for 2 minutes. Do not share this code.")
    msg['Subject'] = "Smart Attendance OTP Verification"
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = recipient_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [recipient_email], msg.as_string())
