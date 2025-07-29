from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import time, datetime


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str]=None
    cuisine_type:str
    address: str 
    phone_number: str 
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
        orm_mode = True