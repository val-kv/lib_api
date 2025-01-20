from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta

from select import select

from app.models import Reader
from app.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

# Конфигурация JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 пароль
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic модели для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    email: str

class User(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

# Функции для работы с паролями
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для создания JWT токенов
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Получение текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(SessionLocal)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id, email=payload.get("email"))
    except JWTError:
        raise credentials_exception
    user = await db.get(Reader, token_data.id)
    if user is None:
        raise credentials_exception
    return user

# Функция для получения пользователя по email
async def get_user_by_email(email: str, db: AsyncSession = Depends(SessionLocal)):
    return await db.execute(select(Reader).filter(Reader.email == email)).scalars().first()
