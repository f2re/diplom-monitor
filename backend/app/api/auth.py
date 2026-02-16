from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=schemas.user.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.user.User).filter(models.user.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.user.UserOut)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = db.query(models.user.User).filter(models.user.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    if user_in.emoji:
        existing_emoji = db.query(models.user.User).filter(
            models.user.User.emoji == user_in.emoji,
            models.user.User.is_active == True
        ).first()
        if existing_emoji:
            raise HTTPException(status_code=400, detail="Этот эмодзи уже занят другим участником")
    
    # Check if this is the first user
    user_count = db.query(models.user.User).count()
    is_superuser = user_count == 0

    db_user = models.user.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        start_date=user_in.start_date,
        deadline=user_in.deadline,
        emoji=user_in.emoji,
        is_superuser=is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=schemas.user.UserOut)
def read_user_me(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/telegram", response_model=schemas.user.Token)
def login_telegram(
    *,
    db: Session = Depends(deps.get_db),
    telegram_data: schemas.user.TelegramAuth,
) -> Any:
    """
    Login with Telegram.
    """
    if not security.verify_telegram_hash(telegram_data.model_dump(), settings.TELEGRAM_BOT_TOKEN):
        raise HTTPException(status_code=400, detail="Invalid Telegram hash")
    
    # Check if user exists by telegram_id
    user = db.query(models.user.User).filter(models.user.User.telegram_id == telegram_data.id).first()
    
    if not user:
        # Check if this is the first user
        user_count = db.query(models.user.User).count()
        is_superuser = user_count == 0

        # Create new user
        full_name = f"{telegram_data.first_name or ''} {telegram_data.last_name or ''}".strip()
        user = models.user.User(
            telegram_id=telegram_data.id,
            full_name=full_name or telegram_data.username,
            is_active=True,
            is_superuser=is_superuser,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use telegram_id as sub if email is not available
    token_subject = user.email if user.email else f"tg_{user.telegram_id}"
    
    return {
        "access_token": security.create_access_token(
            token_subject, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }