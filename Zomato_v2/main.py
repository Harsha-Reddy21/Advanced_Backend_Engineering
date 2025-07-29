from fastapi import FastAPI
from contextlib import asynccontextmanager
import models, database, routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

app.include_router(routes.restaurants_router)
app.include_router(routes.menu_items_router)

