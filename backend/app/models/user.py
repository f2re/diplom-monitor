from sqlalchemy import Column, Integer, String, Date, Boolean, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, index=True)
    is_active = Column(Boolean(), default=True)
    
    # Profile settings
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    emoji = Column(String, default="🎓")

    # Relationships
    week_progressions = relationship("WeekProgress", back_populates="user", cascade="all, delete-orphan")
    special_periods = relationship("SpecialPeriod", back_populates="user", cascade="all, delete-orphan")