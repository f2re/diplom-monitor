from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SpecialPeriod(Base):
    __tablename__ = "special_periods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    period_type = Column(String, nullable=False) # e.g., 'vacation', 'business_trip', 'other'
    description = Column(String, nullable=True)

    user = relationship("User", back_populates="special_periods")
