from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, delete
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
import models, schemas


async def create_restaurant(db, restaurant:schemas.RestaurantCreate):
    new_restaurant=models.Restaurant(**restaurant.dict())
    db.add(new_restaurant)
    try:
        await db.commit()
        await db.refresh(new_restaurant)
        return new_restaurant
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

async def get_restaurant(db, restaurant_id:int):
    result=await db.execute(select(models.Restaurant).where(models.Restaurant.id==restaurant_id))
    restaurant=result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant

async def get_all_restaurants(db,skip:int=0,limit:int=10):
    result=await db.execute(select(models.Restaurant).offset(skip).limit(limit))
    return result.scalars().all()

async def update_restaurant(db, restaurant_id:int, restaurant_data:schemas.RestaurantUpdate):
    query=select(models.Restaurant).where(models.Restaurant.id==restaurant_id)
    result=await db.execute(query)
    db_restaurant=result.scalar_one_or_none()
    if not db_restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    for key,value in restaurant_data.dict().items():
        setattr(db_restaurant, key, value)

    
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

async def delete_restaurant(db, restaurant_id:int):
    result=await db.execute(select(models.Restaurant).where(models.Restaurant.id==restaurant_id))
    restaurant=result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    

    await db.delete(restaurant)
    await db.commit()
    return {"message": "Restaurant deleted successfully"}


async def search_by_cuisine(db, cuisine_type:str):
    result=await db.execute(select(models.Restaurant).where(models.Restaurant.cuisine_type.ilike(f"%{cuisine_type}%")))
    return result.scalars().all()

async def get_active_restaurants(db):
    result=await db.execute(select(models.Restaurant).where(models.Restaurant.is_active==True))
    return result.scalars().all()