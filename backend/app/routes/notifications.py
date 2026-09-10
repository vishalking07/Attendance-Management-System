from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import TokenData
from app.services.auth_service import get_current_user
from app.services.notification_service import get_user_notifications, create_notification
from app.routes.users_data import mock_users_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def fetch_notifications(current_user: TokenData = Depends(get_current_user)):
    return await get_user_notifications(current_user.user_id)

@router.post("/broadcast")
async def broadcast_announcement(
    title: str,
    message: str,
    target_role: str = "ALL",
    current_user: TokenData = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "HOD"]:
        raise HTTPException(status_code=403, detail="Only Admin or HOD can send broad announcements.")

    await create_notification(
        user_id="ALL",
        title=f"📢 Announcement: {title}",
        message=message,
        notification_type="INFO"
    )
    return {"status": "success", "message": "Announcement broadcast successfully."}
