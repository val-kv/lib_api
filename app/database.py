# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = "postgresql+asyncpg://val_k:1986@localhost/lib_api"

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Сессия для взаимодействия с базой данных
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:  # Используем begin() для начала транзакции
        await conn.run_sync(Base.metadata.create_all)
