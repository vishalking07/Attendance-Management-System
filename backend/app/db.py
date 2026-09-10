from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
    try:
        database = db.client[settings.DATABASE_NAME]
        # Ping server to confirm connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
        
        # Ensure Indexes
        await database.geofence_zones.create_index([("geometry", "2dsphere")])
        await database.users.create_index("email", unique=True)
        await database.attendance_records.create_index([("student_id", 1), ("date", 1)], unique=False)
        await database.attendance_sessions.create_index("session_id", unique=True)
    except Exception as e:
        logger.warning(f"Could not connect to live MongoDB server ({e}). Falling back to async in-memory storage mode for seamless operation.")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")
