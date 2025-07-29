from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Time, DateTime, func
from database import Base


class Restaurant(Base):
    __tablename__="restaurants"


    id=Column(Integer, primary_key=True, index=True)
    name=Column(String(100), unique=True, nullable=False)
    description=Column(Text, nullable=False)
    cuisine_type=Column(String, nullable=False)
    location=Column(String, nullable=False)
    rating=Column(Float, default=0.0)
    is_active=Column(Boolean, default=True)
    opening_time=Column(Time, nullable=False)
    closing_time=Column(Time, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True),  onupdate=func.now())


