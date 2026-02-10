from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    emoji: Optional[str] = "🎓"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    emoji: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
