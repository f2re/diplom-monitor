from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Any
from datetime import date

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    emoji: Optional[str] = "🎓"
    is_superuser: bool = False

    @field_validator("start_date", "deadline", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    emoji: Optional[str] = None
    password: Optional[str] = None
    is_superuser: Optional[bool] = None

    @field_validator("start_date", "deadline", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

class UserOut(UserBase):
    id: int
    is_active: bool
    telegram_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    id: int
    full_name: Optional[str] = None
    emoji: Optional[str] = None

    class Config:
        from_attributes = True

class UserPublicProfile(UserPublic):
    start_date: Optional[date] = None
    deadline: Optional[date] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

class TelegramAuth(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str
