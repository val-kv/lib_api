from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Genre
from app.database import SessionLocal
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic schema for Genre
class GenreCreate(BaseModel):
    name: str

class GenreRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

@router.post("/", response_model=GenreRead)
async def create_genre(genre: GenreCreate, db: AsyncSession = Depends(get_db)):
    existing_genre = await db.execute(select(Genre).where(Genre.name == genre.name))
    if existing_genre.scalars().first():
        raise HTTPException(status_code=400, detail="Genre already exists")

    new_genre = Genre(name=genre.name)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre

@router.get("/", response_model=List[GenreRead])
async def get_genres(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genre).offset(skip).limit(limit))
    genres = result.scalars().all()
    return genres
