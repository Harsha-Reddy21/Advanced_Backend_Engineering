from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud, schemas, database
from utils.business_logic import calculate_restaurant_analytics

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/restaurants/{restaurant_id}", response_model=List[schemas.ReviewWithDetails])
async def get_restaurant_reviews(
    restaurant_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db)
):
    await crud.get_restaurant(db, restaurant_id)
    
    reviews = await crud.get_restaurant_reviews(db, restaurant_id, skip, limit)
    
    return [
        schemas.ReviewWithDetails(
            id=review.id,
            customer_id=review.customer_id,
            restaurant_id=review.restaurant_id,
            order_id=review.order_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            customer_name=review.customer.name,
            restaurant_name=""  # Will be filled by restaurant name
        )
        for review in reviews
    ]


@router.get("/restaurants/{restaurant_id}/summary")
async def get_restaurant_review_summary(
    restaurant_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    restaurant = await crud.get_restaurant(db, restaurant_id)
    
    reviews = await crud.get_restaurant_reviews(db, restaurant_id, 0, 100)
    
    if not reviews:
        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "recent_reviews": []
        }
    
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_rating = 0
    
    for review in reviews:
        rating_counts[review.rating] += 1
        total_rating += review.rating
    
    average_rating = total_rating / len(reviews) if reviews else 0.0
    
    recent_reviews = [
        {
            "id": review.id,
            "customer_name": review.customer.name,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        }
        for review in reviews[:5]
    ]
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.name,
        "total_reviews": len(reviews),
        "average_rating": round(average_rating, 2),
        "rating_distribution": rating_counts,
        "recent_reviews": recent_reviews
    }


@router.get("/customers/{customer_id}", response_model=List[schemas.ReviewOut])
async def get_customer_reviews(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(database.get_db)
):
    await crud.get_customer(db, customer_id)
    
    return await crud.get_customer_reviews(db, customer_id, skip, limit)


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(database.get_db)
):  
    from sqlalchemy.future import select
    from sqlalchemy.orm import joinedload
    import models
    
    result = await db.execute(
        select(models.Review)
        .options(
            joinedload(models.Review.customer),
            joinedload(models.Review.restaurant),
            joinedload(models.Review.order)
        )
        .where(models.Review.id == review_id)
    )
    
    review = result.scalar_one_or_none()
    if not review:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at,
        "customer": {
            "id": review.customer.id,
            "name": review.customer.name
        },
        "restaurant": {
            "id": review.restaurant.id,
            "name": review.restaurant.name,
            "cuisine_type": review.restaurant.cuisine_type
        },
        "order": {
            "id": review.order.id,
            "total_amount": review.order.total_amount,
            "order_date": review.order.order_date
        }
    } 