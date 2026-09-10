import jwt
import hashlib
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models.schemas import TokenData, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_password_hash(password: str) -> str:
    # Use SHA-256 salted hash for clean, fast, error-free password verification
    salt = "bioxai_salt_2026_"
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        department_id: str = payload.get("department_id")
        mentor_id: str = payload.get("mentor_id")
        if user_id is None or role is None:
            raise credentials_exception
        return TokenData(
            user_id=user_id,
            role=UserRole(role),
            department_id=department_id,
            mentor_id=mentor_id
        )
    except jwt.PyJWTError:
        raise credentials_exception

def require_roles(allowed_roles: list[UserRole]):
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized for this resource"
            )
        return current_user
    return role_checker
