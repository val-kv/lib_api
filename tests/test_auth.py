from http.client import HTTPException

import pytest

from app.auth import get_user_by_email, create_access_token, get_current_user
from app.main import app
from app.models import Reader
from app.database import SessionLocal

from unittest.mock import patch
from datetime import timedelta
from jose import jwt


# Фикстуры для тестов

@pytest.fixture
def fake_user():
    # Это фикстура для создания фейкового пользователя
    return {
        "id": 1,
        "email": "testuser@example.com",
        "password": "testpassword"  # Не забудьте захешировать пароль
    }


@pytest.fixture
async def db_session():
    # Фикстура для создания сессии в базе данных
    async with SessionLocal() as session:
        yield session


@pytest.fixture
def fake_token(fake_user):
    # Создание токена для тестов
    data = {"sub": fake_user["id"], "email": fake_user["email"]}
    access_token = jwt.encode(data, "your_secret_key", algorithm="HS256")
    return access_token


# Тестирование функции получения пользователя по email
@pytest.mark.asyncio
async def test_get_user_by_email(db_session, fake_user):
    # Заполняем базу данных фейковым пользователем
    db_session.add(Reader(email=fake_user["email"], hashed_password="fakehashed"))
    await db_session.commit()

    user = await get_user_by_email(fake_user["email"], db=db_session)
    assert user is not None
    assert user.email == fake_user["email"]


# Тестирование функции получения текущего пользователя с токеном
@pytest.mark.asyncio
@patch("app.auth.get_current_user")  # Патчим функцию get_current_user
async def test_get_current_user(mock_get_current_user, fake_token, fake_user):
    # Заглушка для get_current_user
    mock_get_current_user.return_value = fake_user

    response = await app.get("/some-protected-endpoint", headers={"Authorization": f"Bearer {fake_token}"})

    assert response.status_code == 200
    assert response.json() == fake_user


# Тестирование функции создания токена
def test_create_access_token():
    data = {"sub": 1, "email": "testuser@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=10))

    # Проверяем, что токен был создан и является строкой
    assert isinstance(token, str)
    assert len(token) > 0


# Тестирование получения текущего пользователя с ошибочным токеном
@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException):
        await get_current_user(token=invalid_token, db=db_session)
