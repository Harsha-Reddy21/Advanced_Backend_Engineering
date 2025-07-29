from fastapi import FastAPI
from contextlib import asynccontextmanager
import models, database, routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(
    title="Zomato v3 - Complete Food Delivery System",
    description="Advanced food delivery API with customers, orders, reviews, and analytics",
    version="3.0.0",
    lifespan=lifespan
)


app.include_router(routes.restaurants_router)
app.include_router(routes.menu_items_router)
app.include_router(routes.customers_router)
app.include_router(routes.orders_router)
app.include_router(routes.reviews_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Zomato v3 - Complete Food Delivery System",
        "version": "3.0.0",
        "features": [
            "Restaurant Management",
            "Menu Item Management", 
            "Customer Management",
            "Order Management with Status Workflow",
            "Review System",
            "Analytics and Reporting",
            "Advanced Search and Filtering"
        ],
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}

