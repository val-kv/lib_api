from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# Схема для создания нового читателя
class ReaderCreate(BaseModel):
    email: str
    password: str
    name: str

class ReaderRead(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        orm_mode = True

# Схема для книги
class BookCreate(BaseModel):
    title: str
    description: Optional[str]
    publication_date: Optional[date]
    available_copies: int
    author_ids: List[int]
    genre_ids: List[int]

class BookRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    publication_date: Optional[date]
    available_copies: int
    authors: List[str]
    genres: List[str]

    class Config:
        orm_mode = True

# Схема для заявки на займ
class LoanCreate(BaseModel):
    book_id: int
    reader_id: int

class LoanRead(BaseModel):
    id: int
    book_id: int
    reader_id: int
    loan_date: date
    return_date: Optional[date]

    class Config:
        orm_mode = True