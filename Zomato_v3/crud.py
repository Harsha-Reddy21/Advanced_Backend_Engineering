from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, delete, and_, func
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from decimal import Decimal
from datetime import datetime, timedelta
import models, schemas
from utils.business_logic import (
    calculate_order_total, validate_order_items, validate_status_transition,
    validate_review_eligibility, estimate_delivery_time, validate_restaurant_operating_hours
)


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


async def create_customer(db, customer: schemas.CustomerCreate):
    new_customer = models.Customer(**customer.dict())
    db.add(new_customer)
    try:
        await db.commit()
        await db.refresh(new_customer)
        return new_customer
    except IntegrityError as e:
        await db.rollback()
        if "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def get_customer(db, customer_id: int):
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

async def get_customer_by_email(db, email: str):
    result = await db.execute(select(models.Customer).where(models.Customer.email == email))
    return result.scalar_one_or_none()

async def get_all_customers(db, skip: int = 0, limit: int = 10):
    result = await db.execute(select(models.Customer).offset(skip).limit(limit))
    return result.scalars().all()

async def update_customer(db, customer_id: int, customer_data: schemas.CustomerUpdate):
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    for key, value in customer_data.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    
    try:
        await db.commit()
        await db.refresh(customer)
        return customer
    except IntegrityError as e:
        await db.rollback()
        if "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

async def delete_customer(db, customer_id: int):
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    await db.delete(customer)
    await db.commit()
    return {"message": "Customer deleted successfully"}


async def create_order(db, customer_id: int, order_data: schemas.OrderCreate):
    validate_order_items(order_data.order_items)
    
    restaurant = await get_restaurant(db, order_data.restaurant_id)
    validate_restaurant_operating_hours(restaurant)

    menu_item_ids = [item.menu_item_id for item in order_data.order_items]
    menu_items_query = select(models.MenuItems).where(
        and_(
            models.MenuItems.id.in_(menu_item_ids),
            models.MenuItems.restaurant_id == order_data.restaurant_id,
            models.MenuItems.is_available == True
        )
    )
    menu_items_result = await db.execute(menu_items_query)
    menu_items = menu_items_result.scalars().all()
    
    if len(menu_items) != len(menu_item_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some menu items are not available or don't belong to this restaurant"
        )
    
    menu_prices = {item.id: item.price for item in menu_items}
    total_amount = calculate_order_total(order_data.order_items, menu_prices)
    
    max_prep_time = max(item.preparation_time for item in menu_items)
    estimated_delivery = estimate_delivery_time(max_prep_time)
    
    order_dict = order_data.dict(exclude={'order_items'})
    order_dict.update({
        'customer_id': customer_id,
        'total_amount': total_amount,
        'delivery_time': estimated_delivery
    })
    
    new_order = models.Order(**order_dict)
    db.add(new_order)
    await db.flush()  
    
    for order_item_data in order_data.order_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            menu_item_id=order_item_data.menu_item_id,
            quantity=order_item_data.quantity,
            item_price=menu_prices[order_item_data.menu_item_id],
            special_requests=order_item_data.special_requests
        )
        db.add(order_item)
    
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def get_order(db, order_id: int):
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

async def get_order_with_details(db, order_id: int):
    result = await db.execute(
        select(models.Order)
        .options(
            joinedload(models.Order.customer),
            joinedload(models.Order.restaurant),
            selectinload(models.Order.order_items).joinedload(models.OrderItem.menu_item)
        )
        .where(models.Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

async def update_order_status(db, order_id: int, status_data: schemas.OrderUpdate):
    order = await get_order(db, order_id)
    
    validate_status_transition(order.order_status, status_data.order_status)
    
    for key, value in status_data.dict(exclude_unset=True).items():
        setattr(order, key, value)
    
    await db.commit()
    await db.refresh(order)
    return order

async def get_customer_orders(db, customer_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(models.Order)
        .options(joinedload(models.Order.restaurant))
        .where(models.Order.customer_id == customer_id)
        .order_by(models.Order.order_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_restaurant_orders(db, restaurant_id: int, skip: int = 0, limit: int = 10, status: Optional[models.OrderStatus] = None):
    query = select(models.Order).options(joinedload(models.Order.customer)).where(models.Order.restaurant_id == restaurant_id)
    
    if status:
        query = query.where(models.Order.order_status == status)
    
    query = query.order_by(models.Order.order_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_review(db, customer_id: int, order_id: int, review_data: schemas.ReviewCreate):
    order = await get_order_with_details(db, order_id)
    validate_review_eligibility(order, customer_id)
    
    existing_review_query = select(models.Review).where(
        and_(
            models.Review.order_id == order_id,
            models.Review.customer_id == customer_id
        )
    )
    existing_result = await db.execute(existing_review_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already exists for this order"
        )
    
    new_review = models.Review(
        customer_id=customer_id,
        restaurant_id=order.restaurant_id,
        order_id=order_id,
        **review_data.dict()
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    
    await update_restaurant_rating(db, order.restaurant_id)
    
    return new_review

async def get_restaurant_reviews(db, restaurant_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(models.Review)
        .options(joinedload(models.Review.customer))
        .where(models.Review.restaurant_id == restaurant_id)
        .order_by(models.Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_customer_reviews(db, customer_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(models.Review)
        .options(joinedload(models.Review.restaurant))
        .where(models.Review.customer_id == customer_id)
        .order_by(models.Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_restaurant_rating(db, restaurant_id: int):
    avg_rating_query = select(func.avg(models.Review.rating)).where(models.Review.restaurant_id == restaurant_id)
    result = await db.execute(avg_rating_query)
    avg_rating = result.scalar() or 0.0
    
    restaurant_query = select(models.Restaurant).where(models.Restaurant.id == restaurant_id)
    restaurant_result = await db.execute(restaurant_query)
    restaurant = restaurant_result.scalar_one()
    restaurant.rating = float(avg_rating)
    
    await db.commit()


async def search_restaurants_advanced(
    db,
    cuisine_type: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 10
):
    query = select(models.Restaurant).where(models.Restaurant.is_active == is_active)
    
    if cuisine_type:
        query = query.where(models.Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
    
    if location:
        query = query.where(models.Restaurant.location.ilike(f"%{location}%"))
    
    if min_rating:
        query = query.where(models.Restaurant.rating >= min_rating)
    
    query = query.order_by(models.Restaurant.rating.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_orders_by_date_range(
    db,
    restaurant_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[models.OrderStatus] = None,
    skip: int = 0,
    limit: int = 10
):
    
    query = select(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.restaurant)
    )
    
    if restaurant_id:
        query = query.where(models.Order.restaurant_id == restaurant_id)
    
    if customer_id:
        query = query.where(models.Order.customer_id == customer_id)
    
    if start_date:
        query = query.where(models.Order.order_date >= start_date)
    
    if end_date:
        query = query.where(models.Order.order_date <= end_date)
    
    if status:
        query = query.where(models.Order.order_status == status)
    
    query = query.order_by(models.Order.order_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

