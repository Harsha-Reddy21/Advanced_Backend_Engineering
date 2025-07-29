from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Time, DateTime, func, ForeignKey, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from database import Base


class Restaurant(Base):
    __tablename__="restaurants"


    id=Column(Integer, primary_key=True, index=True)
    name=Column(String(100), unique=True, nullable=False)
    description=Column(Text, nullable=False)
    cuisine_type=Column(String, nullable=False)
    address=Column(String, nullable=False)
    phone_number=Column(String, nullable=False)
    location=Column(String, nullable=False)
    rating=Column(Float, default=0.0)
    is_active=Column(Boolean, default=True)
    opening_time=Column(Time, nullable=False)
    closing_time=Column(Time, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True),  onupdate=func.now())


    menu_items=relationship("MenuItems", back_populates="restaurant", cascade="all, delete-orphan")




class MenuItems(Base):
    __tablename__="menu_items"


    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    description=Column(Text, nullable=False)
    price=Column(DECIMAL(10, 2), nullable=False)
    category=Column(String, nullable=False)
    is_vegetarian=Column(Boolean, default=False)
    is_vegan=Column(Boolean, default=False)
    is_available=Column(Boolean, default=True)
    preparation_time=Column(Integer, nullable=False)
    restaurant_id=Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"))
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True), onupdate=func.now())

    restaurant=relationship("Restaurant", back_populates="menu_items")