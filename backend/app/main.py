from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.services.scheduler_service import start_scheduler, shutdown_scheduler
from app.services.ml_service import train_risk_prediction_model

# Import API Routers
from app.routes import (
    auth, users, departments, geofence, attendance,
    otp, corrections, leaves, predictions, admin, notifications,
    prognosis, smart_pass, counseling_ai, ledger
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Smart Attendance & Risk Prediction System Backend...")
    await connect_to_mongo()
    start_scheduler()
    train_risk_prediction_model()  # Initialize & fit XGBoost model
    
    # Auto-seed mock data for immediate demo readiness
    from seed import seed_database_data
    seed_database_data()

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()
    await close_mongo_connection()

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(departments.router, prefix=settings.API_V1_STR)
app.include_router(geofence.router, prefix=settings.API_V1_STR)
app.include_router(attendance.router, prefix=settings.API_V1_STR)
app.include_router(otp.router, prefix=settings.API_V1_STR)
app.include_router(corrections.router, prefix=settings.API_V1_STR)
app.include_router(leaves.router, prefix=settings.API_V1_STR)
app.include_router(predictions.router, prefix=settings.API_V1_STR)
app.include_router(prognosis.router, prefix=settings.API_V1_STR)
app.include_router(smart_pass.router, prefix=settings.API_V1_STR)
app.include_router(counseling_ai.router, prefix=settings.API_V1_STR)
app.include_router(ledger.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "online",
        "docs": f"{settings.API_V1_STR}/docs"
    }
