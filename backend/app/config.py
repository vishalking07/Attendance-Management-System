from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Attendance & Risk Prediction System"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Config
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "bio_xai_attendance_db"
    
    # Auth JWT Config
    JWT_SECRET: str = "bioxai_super_secret_jwt_key_2026_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Biometrics & OTP Config
    FACE_CONFIDENCE_THRESHOLD: float = 0.60  # Minimum face match score
    ADAPTIVE_OTP_CONFIDENCE_THRESHOLD: float = 0.85  # Above this, OTP is auto-bypassed unless mandatory
    OTP_VALIDITY_SECONDS: int = 120
    
    # Daily Auto-Absence Cutoff (24h format HH:MM)
    DAILY_ABSENCE_CUTOFF_TIME: str = "09:30"
    
    # SMTP / Email Config for OTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@bioxai.edu"

    class Config:
        env_file = ".env"

settings = Settings()
