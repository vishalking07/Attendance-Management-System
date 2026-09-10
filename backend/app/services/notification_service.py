from datetime import datetime
import logging
from typing import List, Dict, Any
from app.db import get_database

logger = logging.getLogger(__name__)

# In-memory notifications cache for instant dev access
in_memory_notifications: List[Dict[str, Any]] = []
in_memory_audit_logs: List[Dict[str, Any]] = []

async def create_notification(user_id: str, title: str, message: str, notification_type: str = "INFO"):
    notif = {
        "id": f"notif_{len(in_memory_notifications) + 1}",
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notification_type,  # INFO, WARNING, ALERT, SUCCESS
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    in_memory_notifications.insert(0, notif)
    
    try:
        db = await get_database()
        await db.notifications.insert_one(notif)
    except Exception as e:
        logger.debug(f"DB insert notification error: {e}")
    return notif

async def get_user_notifications(user_id: str) -> List[Dict[str, Any]]:
    # Combine in-memory and database
    user_notifs = [n for n in in_memory_notifications if n.get("user_id") == user_id or n.get("user_id") == "ALL"]
    return user_notifs[:20]

async def log_audit_event(actor_id: str, actor_name: str, action: str, target: str, details: str = ""):
    event = {
        "id": f"audit_{len(in_memory_audit_logs) + 1}",
        "actor_id": actor_id,
        "actor_name": actor_name,
        "action": action,
        "target": target,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    in_memory_audit_logs.insert(0, event)
    logger.info(f"📜 [AUDIT LOG] {actor_name} ({actor_id}) -> {action} on {target}: {details}")
    try:
        db = await get_database()
        await db.audit_logs.insert_one(event)
    except Exception as e:
        logger.debug(f"DB insert audit log error: {e}")
    return event
