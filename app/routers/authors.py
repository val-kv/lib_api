from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Author
from app.database import SessionLocal
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic schema for Author
class AuthorCreate(BaseModel):
    name: str
    biography: str | None
    birth_date: str | None

class AuthorRead(BaseModel):
    id: int
    name: str
    biography: str | None
    birth_date: str | None

    class Config:
        orm_mode = True

@router.post("/", response_model=AuthorRead)
async def create_author(author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    # Проверка, существует ли автор с таким же именем
    existing_author = await db.execute(select(Author).where(Author.name == author.name))
    if existing_author.scalars().first():
        raise HTTPException(status_code=400, detail="Author already exists")

    # Создание нового автора
    new_author = Author(
        name=author.name,
        biography=author.biography,
        birth_date=author.birth_date,
    )
    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)
    return new_author

@router.get("/", response_model=List[AuthorRead])
async def get_authors(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).offset(skip).limit(limit))
    authors = result.scalars().all()
    return authors

@router.get("/{author_id}", response_model=AuthorRead)
async def get_author(author_id: int, db: AsyncSession = Depends(get_db)):
    # Получаем автора по ID
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@router.put("/{author_id}", response_model=AuthorRead)
async def update_author(author_id: int, author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    # Получаем автора по ID
    db_author = await db.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Обновляем информацию об авторе
    db_author.name = author.name
    db_author.biography = author.biography
    db_author.birth_date = author.birth_date

    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    return db_author

@router.delete("/{author_id}")
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db)):
    # Получаем автора по ID
    db_author = await db.get(Author, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Удаляем автора
    await db.delete(db_author)
    await db.commit()
    return {"message": "Author deleted successfully"}
