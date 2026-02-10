from pydantic import BaseModel
from datetime import date
from typing import Optional

class WeekProgressBase(BaseModel):
    week_start_date: date
    is_completed: bool = False
    note: Optional[str] = None

class WeekProgressCreate(WeekProgressBase):
    pass

class WeekProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    note: Optional[str] = None

class WeekProgressOut(WeekProgressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
