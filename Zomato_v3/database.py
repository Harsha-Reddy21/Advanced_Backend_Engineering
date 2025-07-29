
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine=create_async_engine(DATABASE_URL, echo=True)
SessionLocal=sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base=declarative_base()







async def get_db():
    async with SessionLocal() as session:
        yield session







