"""ASTRA Auth Router - Login, Register, User Management."""

from datetime import datetime, timezone, timedelta
import random
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User, UserRole
from backend.schemas.auth import UserCreate, UserResponse, Token, OTPResponse, OTPVerify
from backend.middleware.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_role
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Union[Token, OTPResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return OTP requirement."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate OTP
    otp = f"{random.randint(100000, 999999)}"
    user.otp_secret = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    # PRINT OTP TO CONSOLE FOR DEV
    print(f"\n\n==========================================")
    print(f"OTP for {user.username}: {otp}")
    print(f"==========================================\n\n")

    return OTPResponse(
        requires_otp=True,
        username=user.username,
        message=f"OTP sent to {user.email}. (Check server logs, OTP: {otp})"
    )


@router.post("/verify-otp", response_model=Token)
async def verify_otp(
    otp_data: OTPVerify,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == otp_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
        
    if not user.otp_secret or not user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP not requested")
        
    if datetime.now(timezone.utc) > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
        
    if user.otp_secret != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Clear OTP
    user.otp_secret = None
    user.otp_expires_at = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value if isinstance(user.role, UserRole) else user.role}
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        badge_number=user_data.badge_number,
        police_station=user_data.police_station,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user)


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/setup-admin", response_model=UserResponse)
async def setup_admin(db: Session = Depends(get_db)):
    """One-time setup: create the initial admin user. Only works if no users exist."""
    if db.query(User).count() > 0:
        raise HTTPException(status_code=400, detail="Admin already exists. Use /register.")

    admin = User(
        username="admin",
        email="admin@astra.local",
        full_name="ASTRA Administrator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return UserResponse.model_validate(admin)
