from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Time, DateTime, func, ForeignKey, DECIMAL, DATETIME, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


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
    orders=relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    reviews=relationship("Review", back_populates="restaurant", cascade="all, delete-orphan")




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
    order_items=relationship("OrderItem", back_populates="menu_item", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="customer", cascade="all, delete-orphan")


class OrderStatus(enum.Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.PLACED)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    delivery_address = Column(Text, nullable=False)
    special_instructions = Column(Text)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    delivery_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    item_price = Column(DECIMAL(10, 2), nullable=False)  # Price at time of order
    special_requests = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItems", back_populates="order_items")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("Customer", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")