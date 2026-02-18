from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

# Пул доступных эмоджи для автоназначения
EMOJI_POOL: List[str] = [
    "🎓", "🚀", "⭐", "🔥", "🌟",
    "💪", "🦅", "🌈", "⚡", "🎯",
    "🐉", "🦄", "🐼", "🦊", "🐮",
    "🐻", "🐯", "🐺", "🦁", "🐸",
    "🐢", "🐧", "🦋", "🐳", "🐙",
    "🌵", "🌲", "🌻", "🍀", "🍎",
]


def assign_free_emoji(db: Session, preferred: str = None) -> str:
    """
    Назначает первый свободный эмоджи из пула.
    Если передан preferred и он свободен — возвращает его.
    Иначе ищет следующий свободный в пуле.
    """
    # Загружаем все занятые эмоджи одним запросом
    taken = set(
        row[0] for row in
        db.query(models.user.User.emoji)
        .filter(models.user.User.is_active == True, models.user.User.emoji != None)
        .all()
    )

    # Сначала пробуем preferred
    if preferred and preferred not in taken:
        return preferred

    # Ищем первый свободный из пула
    for emoji in EMOJI_POOL:
        if emoji not in taken:
            return emoji

    # Если все заняты — генерируем уникальный по счётчику пользователей
    user_count = db.query(models.user.User).count()
    return f"🎓{user_count}"


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
    Create new user. Auto-assigns a free emoji if preferred is taken.
    """
    # Проверяем дубликат email
    existing = db.query(models.user.User).filter(models.user.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует",
        )

    # Автоназначаем свободный эмоджи (если preferred занят — возьмем следующий)
    emoji = assign_free_emoji(db, preferred=user_in.emoji)

    # Первый зарегистрировавшийся — админ
    user_count = db.query(models.user.User).count()
    is_superuser = user_count == 0

    db_user = models.user.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        start_date=user_in.start_date,
        deadline=user_in.deadline,
        emoji=emoji,
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
    Login or register via Telegram. Auto-assigns emoji.
    """
    if not security.verify_telegram_hash(telegram_data.model_dump(), settings.TELEGRAM_BOT_TOKEN):
        raise HTTPException(status_code=400, detail="Invalid Telegram hash")

    # Ищем существующего по telegram_id
    user = db.query(models.user.User).filter(models.user.User.telegram_id == telegram_data.id).first()

    if not user:
        user_count = db.query(models.user.User).count()
        is_superuser = user_count == 0

        full_name = f"{telegram_data.first_name or ''} {telegram_data.last_name or ''}".strip()
        emoji = assign_free_emoji(db)

        user = models.user.User(
            telegram_id=telegram_data.id,
            full_name=full_name or telegram_data.username,
            emoji=emoji,
            is_active=True,
            is_superuser=is_superuser,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_subject = user.email if user.email else f"tg_{user.telegram_id}"

    return {
        "access_token": security.create_access_token(
            token_subject, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/config", response_model=schemas.config.ConfigResponse)
def get_config() -> Any:
    """
    Get public configuration.
    """
    return schemas.config.ConfigResponse(
        telegram_bot_name=settings.TELEGRAM_BOT_NAME
    )
