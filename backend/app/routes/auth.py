from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import LoginRequest, Token, UserResponse, UserRole
from app.services.auth_service import create_access_token, verify_password, get_current_user
from app.services.notification_service import log_audit_event
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Auth"])

# In-memory user store for fast fallback / demo
from app.routes.users_data import mock_users_db

@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest):
    email = credentials.email.lower()
    user = mock_users_db.get(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT Token with embedded role & scope claims
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "department_id": user.get("department_id"),
        "mentor_id": user.get("mentor_id")
    }
    access_token = create_access_token(data=token_data)

    await log_audit_event(
        actor_id=user["id"],
        actor_name=user["name"],
        action="USER_LOGIN",
        target=user["role"],
        details=f"Successful login for {user['email']}"
    )

    user_payload = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department_id": user.get("department_id"),
        "mentor_id": user.get("mentor_id"),
        "profile_photo": user.get("profile_photo")
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_payload
    }

@router.get("/me")
async def get_me(current_user: Any = Depends(get_current_user)):
    user = None
    for u in mock_users_db.values():
        if u["id"] == current_user.user_id:
            user = u
            break
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department_id": user.get("department_id"),
        "mentor_id": user.get("mentor_id"),
        "profile_photo": user.get("profile_photo")
    }
