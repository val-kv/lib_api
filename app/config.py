import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # URL базы данных PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/library_db"

    # Настройки JWT
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


# Инициализация настроек
settings = Settings()
