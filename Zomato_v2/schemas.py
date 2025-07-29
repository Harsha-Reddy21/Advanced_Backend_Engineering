from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import time, datetime


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











