from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import time, datetime
from decimal import Decimal
from enum import Enum


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str]=None
    cuisine_type:str
    address: str 
    phone_number: str 
    location: str
    rating: float = Field(default=0.0, ge=0, le=5)
    is_active: bool = True 
    opening_time: time 
    closing_time: time 

    @validator("phone_number")
    def validate_phone(cls,v):
        import re 
        if not re.match(r'^\+?\d{10,15}$', v):
            raise ValueError("Invalid phone number format")
        return v
    
class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(RestaurantBase):
    pass

class RestaurantOut(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True



class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str]=None
    price: float = Field(..., ge=0)
    category: str
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_available: bool = True
    preparation_time: int = Field(..., ge=0)
    

class MenuItemCreate(MenuItemBase): pass 
class MenuItemUpdate(MenuItemBase): pass  



class MenuItemOut(MenuItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MenuItemWithRestaurant(MenuItemOut):
    restaurant: RestaurantOut


class RestaurantWithMenu(RestaurantOut):
    menu_items: List[MenuItemOut]



class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=10)
    is_active: bool = True

    @validator("phone_number")
    def validate_phone(cls, v):
        import re
        if not re.match(r'^\+?\d{10,15}$', v):
            raise ValueError("Invalid phone number format")
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True



class OrderStatusEnum(str, Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"



class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., ge=1)
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    item_price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItemWithMenu(OrderItemOut):
    menu_item: MenuItemOut



class OrderBase(BaseModel):
    delivery_address: str = Field(..., min_length=10)
    special_instructions: Optional[str] = None
    delivery_time: Optional[datetime] = None

class OrderCreate(OrderBase):
    restaurant_id: int
    order_items: List[OrderItemCreate] = Field(..., min_items=1)

class OrderUpdate(BaseModel):
    order_status: OrderStatusEnum
    delivery_time: Optional[datetime] = None
    special_instructions: Optional[str] = None

class OrderOut(OrderBase):
    id: int
    customer_id: int
    restaurant_id: int
    order_status: OrderStatusEnum
    total_amount: Decimal
    order_date: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class OrderWithDetails(OrderOut):
    customer: CustomerOut
    restaurant: RestaurantOut
    order_items: List[OrderItemWithMenu]

class OrderSummary(BaseModel):
    id: int
    restaurant_name: str
    order_status: OrderStatusEnum
    total_amount: Decimal
    order_date: datetime

    class Config:
        from_attributes = True



class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    customer_id: int
    restaurant_id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewWithDetails(ReviewOut):
    customer_name: str
    restaurant_name: str



class RestaurantAnalytics(BaseModel):
    total_orders: int
    total_revenue: Decimal
    average_rating: float
    popular_items: List[dict]
    orders_by_status: dict

class CustomerAnalytics(BaseModel):
    total_orders: int
    total_spent: Decimal
    favorite_restaurants: List[dict]
    order_frequency: dict



class CustomerWithOrders(CustomerOut):
    orders: List[OrderSummary]

class RestaurantWithReviews(RestaurantOut):
    reviews: List[ReviewOut]
    average_rating: float
    total_reviews: int











