from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud, schemas, database

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("/", response_model=schemas.RestaurantOut, status_code=201)
async def create(restaurant:schemas.RestaurantCreate, db:AsyncSession=Depends(database.get_db)):
    return await crud.create_restaurant(db, restaurant)

@router.get("/",response_model=List[schemas.RestaurantOut])
async def list_all(skip:int=0, limit:int=10, db:AsyncSession=Depends(database.get_db)):
    return await crud.get_all_restaurants(db, skip, limit)



@router.get("/{restaurant_id}", response_model=schemas.RestaurantOut)
async def get_one(restaurant_id:int, db:AsyncSession=Depends(database.get_db)):
    return await crud.get_restaurant(db, restaurant_id)


@router.put("/{restaurant_id}", response_model=schemas.RestaurantOut)
async def update(restaurant_id:int, restaurant_data:schemas.RestaurantUpdate, db:AsyncSession=Depends(database.get_db)):
    return await crud.update_restaurant(db, restaurant_id, restaurant_data)

@router.delete("/{restaurant_id}", status_code=204)
async def delete(restaurant_id:int, db:AsyncSession=Depends(database.get_db)):
    return await crud.delete_restaurant(db, restaurant_id)


@router.get("/search", response_model=List[schemas.RestaurantOut])
async def search_by_cuisine(cuisine_type:str, db:AsyncSession=Depends(database.get_db)):
    return await crud.search_by_cuisine(db, cuisine_type)


@router.get("/active", response_model=List[schemas.RestaurantOut])
async def get_active(db:AsyncSession=Depends(database.get_db)):
    return await crud.get_active_restaurants(db)

@router.post("/{restaurant_id}/menu-items/", response_model=schemas.MenuItemOut)
async def add_menu_item(restaurant_id: int, item: schemas.MenuItemCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_menu_item(db, restaurant_id, item)

@router.get("/{restaurant_id}/menu", response_model=List[schemas.MenuItemOut])
async def get_menu(restaurant_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_menu_by_restaurant(db, restaurant_id)

@router.get("/{restaurant_id}/with-menu", response_model=schemas.RestaurantWithMenu)
async def get_restaurant_with_menu(restaurant_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_restaurant_with_menu(db, restaurant_id)
