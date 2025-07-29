from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import crud, schemas, database, models

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/{order_id}", response_model=schemas.OrderWithDetails)
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """Get detailed order information including customer, restaurant, and order items"""
    order = await crud.get_order_with_details(db, order_id)
    
    # Transform to response format
    return schemas.OrderWithDetails(
        id=order.id,
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id,
        order_status=order.order_status,
        total_amount=order.total_amount,
        delivery_address=order.delivery_address,
        special_instructions=order.special_instructions,
        order_date=order.order_date,
        delivery_time=order.delivery_time,
        created_at=order.created_at,
        updated_at=order.updated_at,
        customer=schemas.CustomerOut.from_orm(order.customer),
        restaurant=schemas.RestaurantOut.from_orm(order.restaurant),
        order_items=[
            schemas.OrderItemWithMenu(
                id=item.id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                item_price=item.item_price,
                special_requests=item.special_requests,
                created_at=item.created_at,
                menu_item=schemas.MenuItemOut.from_orm(item.menu_item)
            )
            for item in order.order_items
        ]
    )


@router.put("/{order_id}/status", response_model=schemas.OrderOut)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    """Update order status (with business logic validation)"""
    return await crud.update_order_status(db, order_id, status_update)


@router.get("/", response_model=List[schemas.OrderOut])
async def list_orders(
    restaurant_id: Optional[int] = Query(None, description="Filter by restaurant"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    status: Optional[schemas.OrderStatusEnum] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter orders from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter orders until this date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db)
):
    """Get orders with various filters"""
    # Convert enum to model enum if provided
    model_status = None
    if status:
        model_status = models.OrderStatus(status.value)
    
    orders = await crud.get_orders_by_date_range(
        db, restaurant_id, customer_id, start_date, end_date, model_status, skip, limit
    )
    
    return [schemas.OrderOut.from_orm(order) for order in orders]


@router.post("/{order_id}/review", response_model=schemas.ReviewOut, status_code=201)
async def add_review(
    order_id: int,
    review_data: schemas.ReviewCreate,
    customer_id: int = Query(..., description="Customer ID adding the review"),
    db: AsyncSession = Depends(database.get_db)
):
    """Add a review for a completed order"""
    return await crud.create_review(db, customer_id, order_id, review_data)


@router.get("/{order_id}/can-review")
async def check_review_eligibility(
    order_id: int,
    customer_id: int = Query(..., description="Customer ID to check eligibility"),
    db: AsyncSession = Depends(database.get_db)
):
    """Check if a customer can review this order"""
    order = await crud.get_order_with_details(db, order_id)
    
    try:
        from utils.business_logic import validate_review_eligibility
        validate_review_eligibility(order, customer_id)
        return {"can_review": True, "message": "Review can be added"}
    except Exception as e:
        return {"can_review": False, "message": str(e)} 