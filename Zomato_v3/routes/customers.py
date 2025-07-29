from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud, schemas, database
from utils.business_logic import calculate_customer_analytics

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=schemas.CustomerOut, status_code=201)
async def create_customer(
    customer: schemas.CustomerCreate, 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.create_customer(db, customer)


@router.get("/", response_model=List[schemas.CustomerOut])
async def list_customers(
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, ge=1, le=100), 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.get_all_customers(db, skip, limit)


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
async def get_customer(
    customer_id: int, 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.get_customer(db, customer_id)


@router.put("/{customer_id}", response_model=schemas.CustomerOut)
async def update_customer(
    customer_id: int, 
    customer_data: schemas.CustomerUpdate, 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.update_customer(db, customer_id, customer_data)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int, 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.delete_customer(db, customer_id)


@router.get("/{customer_id}/orders", response_model=List[schemas.OrderSummary])
async def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db)
):
    orders = await crud.get_customer_orders(db, customer_id, skip, limit)
    return [
        schemas.OrderSummary(
            id=order.id,
            restaurant_name=order.restaurant.name,
            order_status=order.order_status,
            total_amount=order.total_amount,
            order_date=order.order_date
        )
        for order in orders
    ]


@router.post("/{customer_id}/orders", response_model=schemas.OrderOut, status_code=201)
async def place_order(
    customer_id: int,
    order_data: schemas.OrderCreate,
    db: AsyncSession = Depends(database.get_db)
):
    await crud.get_customer(db, customer_id)
    return await crud.create_order(db, customer_id, order_data)


@router.get("/{customer_id}/reviews", response_model=List[schemas.ReviewOut])
async def get_customer_reviews(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.get_customer_reviews(db, customer_id, skip, limit)


@router.get("/{customer_id}/analytics", response_model=schemas.CustomerAnalytics)
async def get_customer_analytics(
    customer_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    await crud.get_customer(db, customer_id)
    return await calculate_customer_analytics(db, customer_id) 