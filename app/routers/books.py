from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Book, Author, Genre
from app.database import SessionLocal
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic schema for Book
class BookCreate(BaseModel):
    title: str
    description: str | None
    publication_date: str
    author_ids: List[int]
    genre_ids: List[int]
    available_copies: int

class BookRead(BaseModel):
    id: int
    title: str
    description: str | None
    publication_date: str
    authors: List[str]
    genres: List[str]
    available_copies: int

    class Config:
        orm_mode = True

@router.post("/", response_model=BookRead)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    authors = await db.execute(select(Author).where(Author.id.in_(book.author_ids)))
    authors = authors.scalars().all()
    if len(authors) != len(book.author_ids):
        raise HTTPException(status_code=400, detail="One or more authors not found")

    genres = await db.execute(select(Genre).where(Genre.id.in_(book.genre_ids)))
    genres = genres.scalars().all()
    if len(genres) != len(book.genre_ids):
        raise HTTPException(status_code=400, detail="One or more genres not found")

    new_book = Book(
        title=book.title,
        description=book.description,
        publication_date=book.publication_date,
        available_copies=book.available_copies,
    )

    new_book.authors.extend(authors)
    new_book.genres.extend(genres)

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return new_book

@router.get("/", response_model=List[BookRead])
async def get_books(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return books

@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book

@router.put("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = await db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    authors = await db.execute(select(Author).where(Author.id.in_(book.author_ids)))
    authors = authors.scalars().all()
    if len(authors) != len(book.author_ids):
        raise HTTPException(status_code=400, detail="One or more authors not found")

    genres = await db.execute(select(Genre).where(Genre.id.in_(book.genre_ids)))
    genres = genres.scalars().all()
    if len(genres) != len(book.genre_ids):
        raise HTTPException(status_code=400, detail="One or more genres not found")

    db_book.title = book.title
    db_book.description = book.description
    db_book.publication_date = book.publication_date
    db_book.available_copies = book.available_copies

    db_book.authors.clear()
    db_book.authors.extend(authors)

    db_book.genres.clear()
    db_book.genres.extend(genres)

    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)

    return db_book

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    db_book = await db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(db_book)
    await db.commit()

    return {"message": "Book deleted successfully"}
