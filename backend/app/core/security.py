from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

PWD_CONTEXT = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)

import hmac
import hashlib

def verify_telegram_hash(data: dict, bot_token: str) -> bool:
    telegram_hash = data.get("hash")
    if not telegram_hash:
        return False
    
    # Sort keys and create data_check_string
    data_list = []
    for key, value in sorted(data.items()):
        if key != "hash" and value is not None:
            data_list.append(f"{key}={value}")
    data_check_string = "\n".join(data_list)
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return hash_value == telegram_hash
