from pydantic import BaseModel
from datetime import date
from typing import Optional

class SpecialPeriodBase(BaseModel):
    start_date: date
    end_date: date
    period_type: str
    description: Optional[str] = None

class SpecialPeriodCreate(SpecialPeriodBase):
    pass

class SpecialPeriodUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period_type: Optional[str] = None
    description: Optional[str] = None

class SpecialPeriodOut(SpecialPeriodBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
