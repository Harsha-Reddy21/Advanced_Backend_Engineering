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



async def create_menu_item(db, restaurant_id:int, menu_item:schemas.MenuItemCreate):
    result=await db.execute(select(models.Restaurant).where(models.Restaurant.id==restaurant_id))
    restaurant=result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    new_menu_item=models.MenuItems(**menu_item.dict(), restaurant_id=restaurant_id)
    db.add(new_menu_item)
    await db.commit()
    await db.refresh(new_menu_item)
    return new_menu_item


async def get_menu_item(db, menu_item_id:int):
    result=await db.execute(select(models.MenuItems).where(models.MenuItems.id==menu_item_id))
    item=result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item

async def get_menu_item_with_restaurant(db, menu_item_id:int):
    result=await db.execute(select(models.MenuItems).options(joinedload(models.MenuItems.restaurant)).where(models.MenuItems.id==menu_item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item

async def get_all_menu_items(db, skip:int=0, limit:int=10):
    result=await db.execute(select(models.MenuItems).offset(skip).limit(limit))
    return result.scalars().all()


async def update_menu_item(db, menu_item_id:int, menu_item_data:schemas.MenuItemUpdate):
    result=await db.execute(select(models.MenuItems).where(models.MenuItems.id==menu_item_id))
    item=result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    
    for key,value in menu_item_data.dict().items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


async def delete_menu_item(db, menu_item_id:int):
    result=await db.execute(select(models.MenuItems).where(models.MenuItems.id==menu_item_id))
    item=result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    
    await db.delete(item)
    await db.commit()
    return {"message": "Menu item deleted successfully"}



async def get_menu_items_by_restaurant(db, restaurant_id:int, skip:int=0, limit:int=10):
    result=await db.execute(select(models.MenuItems).where(models.MenuItems.restaurant_id==restaurant_id).offset(skip).limit(limit))
    return result.scalars().all()


async def restaurant_with_menu_items(db, restaurant_id:int):
    result=await db.execute(select(models.Restaurant).options(joinedload(models.Restaurant.menu_items)).where(models.Restaurant.id==restaurant_id))
    restaurant=result.scalar_one_or_none()


async def get_menu_by_restaurant(db, restaurant_id:int):
    result=await db.execute(select(models.MenuItems).where(models.MenuItems.restaurant_id==restaurant_id))
    return result.scalars().all()

async def get_restaurant_with_menu(db, restaurant_id:int):
    result=await db.execute(select(models.Restaurant).options(joinedload(models.Restaurant.menu_items)).where(models.Restaurant.id==restaurant_id))
    restaurant=result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant

async def search_menu_items(db, category: str, vegetarian: bool = False):
    query = select(models.MenuItems).where(models.MenuItems.category.ilike(f"%{category}%"))
    if vegetarian:
        query = query.where(models.MenuItems.is_vegetarian == True)
    result = await db.execute(query)
    return result.scalars().all()

