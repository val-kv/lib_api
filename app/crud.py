from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Reader, Book, Loan
from app.auth import get_password_hash
from fastapi import HTTPException
from app.schemas import ReaderCreate, ReaderRead, BookCreate, BookRead

# Создание нового читателя
async def create_reader(reader: ReaderCreate, db: AsyncSession):
    existing_reader = await db.execute(select(Reader).filter(Reader.email == reader.email))
    if existing_reader.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(reader.password)
    new_reader = Reader(email=reader.email, hashed_password=hashed_password, name=reader.name)
    db.add(new_reader)
    await db.commit()
    await db.refresh(new_reader)
    return new_reader

# Получение всех читателей
async def get_readers(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Reader).offset(skip).limit(limit))
    readers = result.scalars().all()
    return readers

# Получение читателя по ID
async def get_reader_by_id(reader_id: int, db: AsyncSession):
    reader = await db.get(Reader, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader

# Создание новой книги
async def create_book(book: BookCreate, db: AsyncSession):
    new_book = Book(**book.dict())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

# Получение всех книг
async def get_books(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return books

# Получение книги по ID
async def get_book_by_id(book_id: int, db: AsyncSession):
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Получение всех книг с возвращением модели BookRead
async def get_books_read(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return [BookRead.from_orm(book) for book in books]

# Получение всех читателей с возвращением модели ReaderRead
async def get_readers_read(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Reader).offset(skip).limit(limit))
    readers = result.scalars().all()
    return [ReaderRead.from_orm(reader) for reader in readers]

# Создание новой записи о займе
async def create_loan(book_id: int, reader_id: int, db: AsyncSession):
    # Проверка доступных экземпляров книги
    book = await db.get(Book, book_id)
    if not book or book.available_copies < 1:
        raise HTTPException(status_code=400, detail="Book not available")
    loan = Loan(book_id=book_id, reader_id=reader_id)
    db.add(loan)
    book.available_copies -= 1
    await db.commit()
    await db.refresh(loan)
    return loan
