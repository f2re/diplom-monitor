from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class WeekProgress(Base):
    __tablename__ = "week_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start_date = Column(Date, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="week_progressions")