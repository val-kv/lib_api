import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import context
from app.models import Base  # Модели для миграций
from app.database import DATABASE_URL  # URL для подключения к базе данных
import asyncio

# Устанавливаем путь к текущей директории
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Метаданные для миграций
target_metadata = Base.metadata

# Создаем асинхронный движок
DATABASE_URL = "postgresql+asyncpg://val_k:1986@localhost/lib_api"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Сессия для работы с асинхронным движком
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def run_migrations_online():
    """Запуск миграций в онлайн-режиме с асинхронным соединением"""
    connectable = engine

    # Для асинхронного соединения необходимо использовать run_sync для любых синхронных операций
    async with connectable.connect() as connection:
        # Передаем подключение в Alembic
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        # Для работы с контекстом миграции используем синхронный режим
        async with connection.begin():
            # Запускаем миграции
            await context.run_migrations()

async def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме"""
    url = str(DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    # Генерация миграционных скриптов в оффлайн-режиме
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations():
    """Основная логика для выбора между онлайн- и оффлайн-режимом"""
    if context.is_offline_mode():
        await run_migrations_offline()
    else:
        await run_migrations_online()

# Запуск миграции
async def main():
    await run_migrations()

# Запуск миграции
if __name__ == "__main__":
    asyncio.run(main())
