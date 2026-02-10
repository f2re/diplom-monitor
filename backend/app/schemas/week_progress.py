from pydantic import BaseModel
from datetime import date
from typing import Optional, List

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

class GridStats(BaseModel):
    total_weeks: int
    special_weeks: int
    effective_weeks: int
    completed_weeks: int
    remaining_weeks: int

class GridConfig(BaseModel):
    start_date: Optional[date] = None
    deadline: Optional[date] = None

class UserWeekProgress(BaseModel):
    user_id: int
    emoji: str
    completions: List[date]