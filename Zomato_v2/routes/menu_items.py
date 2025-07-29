from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud, database, schemas

router = APIRouter(prefix="/menu-items", tags=["Menu Items"])

@router.get("/", response_model=List[schemas.MenuItemOut])
async def get_all(db: AsyncSession = Depends(database.get_db)):
    return await crud.get_all_menu_items(db)

@router.get("/{item_id}", response_model=schemas.MenuItemOut)
async def get_one(item_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_menu_item(db, item_id)

@router.get("/{item_id}/with-restaurant", response_model=schemas.MenuItemWithRestaurant)
async def get_with_restaurant(item_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_menu_item_with_restaurant(db, item_id)

@router.put("/{item_id}", response_model=schemas.MenuItemOut)
async def update(item_id: int, data: schemas.MenuItemUpdate, db: AsyncSession = Depends(database.get_db)):
    return await crud.update_menu_item(db, item_id, data)

@router.delete("/{item_id}")
async def delete(item_id: int, db: AsyncSession = Depends(database.get_db)):
    return await crud.delete_menu_item(db, item_id)

@router.get("/search/", response_model=List[schemas.MenuItemOut])
async def search(category: str, vegetarian: bool = False, db: AsyncSession = Depends(database.get_db)):
    return await crud.search_menu_items(db, category, vegetarian)
