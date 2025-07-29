from decimal import Decimal
from typing import List, Dict, Any
from datetime import datetime, timedelta
import models, schemas
from sqlalchemy import func, and_
from sqlalchemy.future import select
from fastapi import HTTPException, status


def calculate_order_total(order_items: List[schemas.OrderItemCreate], menu_items_prices: Dict[int, Decimal]) -> Decimal:
    total = Decimal('0.00')
    for item in order_items:
        if item.menu_item_id not in menu_items_prices:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {item.menu_item_id} not found"
            )
        item_total = menu_items_prices[item.menu_item_id] * item.quantity
        total += item_total
    return total


def validate_order_items(order_items: List[schemas.OrderItemCreate]) -> bool:
    if not order_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    menu_item_ids = [item.menu_item_id for item in order_items]
    if len(menu_item_ids) != len(set(menu_item_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate menu items not allowed. Use quantity instead."
        )
    
    return True


def get_next_order_status(current_status: models.OrderStatus) -> List[models.OrderStatus]:
    status_transitions = {
        models.OrderStatus.PLACED: [models.OrderStatus.CONFIRMED, models.OrderStatus.CANCELLED],
        models.OrderStatus.CONFIRMED: [models.OrderStatus.PREPARING, models.OrderStatus.CANCELLED],
        models.OrderStatus.PREPARING: [models.OrderStatus.OUT_FOR_DELIVERY, models.OrderStatus.CANCELLED],
        models.OrderStatus.OUT_FOR_DELIVERY: [models.OrderStatus.DELIVERED],
        models.OrderStatus.DELIVERED: [],
        models.OrderStatus.CANCELLED: []
    }
    return status_transitions.get(current_status, [])


def validate_status_transition(current_status: models.OrderStatus, new_status: models.OrderStatus) -> bool:
    allowed_statuses = get_next_order_status(current_status)
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {current_status.value} to {new_status.value}"
        )
    return True


def can_add_review(order_status: models.OrderStatus) -> bool:
    return order_status == models.OrderStatus.DELIVERED


def validate_review_eligibility(order: models.Order, customer_id: int) -> bool:
    if order.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own orders"
        )
    
    if not can_add_review(order.order_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be added for delivered orders"
        )
    
    return True


async def calculate_restaurant_analytics(db, restaurant_id: int) -> schemas.RestaurantAnalytics:
    
    orders_query = select(
        func.count(models.Order.id).label('total_orders'),
        func.coalesce(func.sum(models.Order.total_amount), 0).label('total_revenue')
    ).where(models.Order.restaurant_id == restaurant_id)
    
    result = await db.execute(orders_query)
    orders_data = result.fetchone()
    
    rating_query = select(func.avg(models.Review.rating)).where(
        models.Review.restaurant_id == restaurant_id
    )
    rating_result = await db.execute(rating_query)
    avg_rating = rating_result.scalar() or 0.0
    
    status_query = select(
        models.Order.order_status,
        func.count(models.Order.id)
    ).where(
        models.Order.restaurant_id == restaurant_id
    ).group_by(models.Order.order_status)
    
    status_result = await db.execute(status_query)
    orders_by_status = {status.value: count for status, count in status_result.fetchall()}

    popular_items_query = select(
        models.MenuItems.name,
        func.sum(models.OrderItem.quantity).label('total_ordered')
    ).join(
        models.OrderItem, models.MenuItems.id == models.OrderItem.menu_item_id
    ).join(
        models.Order, models.OrderItem.order_id == models.Order.id
    ).where(
        models.Order.restaurant_id == restaurant_id
    ).group_by(
        models.MenuItems.id, models.MenuItems.name
    ).order_by(
        func.sum(models.OrderItem.quantity).desc()
    ).limit(5)
    
    popular_result = await db.execute(popular_items_query)
    popular_items = [
        {"name": name, "total_ordered": count}
        for name, count in popular_result.fetchall()
    ]
    
    return schemas.RestaurantAnalytics(
        total_orders=orders_data.total_orders or 0,
        total_revenue=orders_data.total_revenue or Decimal('0.00'),
        average_rating=float(avg_rating),
        popular_items=popular_items,
        orders_by_status=orders_by_status
    )


async def calculate_customer_analytics(db, customer_id: int) -> schemas.CustomerAnalytics:
    
    orders_query = select(
        func.count(models.Order.id).label('total_orders'),
        func.coalesce(func.sum(models.Order.total_amount), 0).label('total_spent')
    ).where(models.Order.customer_id == customer_id)
    
    result = await db.execute(orders_query)
    orders_data = result.fetchone()
    
    favorite_query = select(
        models.Restaurant.name,
        func.count(models.Order.id).label('order_count'),
        func.sum(models.Order.total_amount).label('total_spent')
    ).join(
        models.Order, models.Restaurant.id == models.Order.restaurant_id
    ).where(
        models.Order.customer_id == customer_id
    ).group_by(
        models.Restaurant.id, models.Restaurant.name
    ).order_by(
        func.count(models.Order.id).desc()
    ).limit(5)
    
    favorite_result = await db.execute(favorite_query)
    favorite_restaurants = [
        {
            "name": name,
            "order_count": count,
            "total_spent": float(total_spent or 0)
        }
        for name, count, total_spent in favorite_result.fetchall()
    ]
    
    frequency_query = select(
        func.strftime('%Y-%m', models.Order.order_date).label('month'),
        func.count(models.Order.id).label('order_count')
    ).where(
        and_(
            models.Order.customer_id == customer_id,
            models.Order.order_date >= datetime.now() - timedelta(days=365)
        )
    ).group_by(
        func.strftime('%Y-%m', models.Order.order_date)
    ).order_by(
        func.strftime('%Y-%m', models.Order.order_date)
    )
    
    frequency_result = await db.execute(frequency_query)
    order_frequency = {
        month: count for month, count in frequency_result.fetchall()
    }
    
    return schemas.CustomerAnalytics(
        total_orders=orders_data.total_orders or 0,
        total_spent=orders_data.total_spent or Decimal('0.00'),
        favorite_restaurants=favorite_restaurants,
        order_frequency=order_frequency
    )


def estimate_delivery_time(preparation_time: int, base_delivery_minutes: int = 30) -> datetime:
    total_minutes = preparation_time + base_delivery_minutes
    return datetime.now() + timedelta(minutes=total_minutes)


def validate_restaurant_operating_hours(restaurant: models.Restaurant) -> bool:
    current_time = datetime.now().time()
    if restaurant.opening_time <= restaurant.closing_time:
        is_open = restaurant.opening_time <= current_time <= restaurant.closing_time
    else:
        is_open = current_time >= restaurant.opening_time or current_time <= restaurant.closing_time
    
    if not is_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Restaurant is closed. Operating hours: {restaurant.opening_time} - {restaurant.closing_time}"
        )
    
    return True 