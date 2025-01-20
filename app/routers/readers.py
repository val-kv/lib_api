from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Reader
from app.database import SessionLocal
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic schema for Reader
class ReaderCreate(BaseModel):
    name: str
    email: str
    password: str

class ReaderRead(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

@router.post("/", response_model=ReaderRead)
async def create_reader(reader: ReaderCreate, db: AsyncSession = Depends(get_db)):
    existing_reader = await db.execute(select(Reader).where(Reader.email == reader.email))
    if existing_reader.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_reader = Reader(
        name=reader.name,
        email=reader.email,
        hashed_password=reader.password  # In production, hash this password
    )
    db.add(new_reader)
    await db.commit()
    await db.refresh(new_reader)
    return new_reader

@router.get("/", response_model=List[ReaderRead])
async def get_readers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reader).offset(skip).limit(limit))
    readers = result.scalars().all()
    return readers
