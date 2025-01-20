from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Loan, Book, Reader
from app.database import SessionLocal
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List

router = APIRouter()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic schema for Loan
class LoanCreate(BaseModel):
    book_id: int
    reader_id: int

class LoanRead(BaseModel):
    id: int
    book_id: int
    reader_id: int
    loan_date: date
    return_date: date | None

    class Config:
        orm_mode = True

@router.post("/", response_model=LoanRead)
async def create_loan(loan: LoanCreate, db: AsyncSession = Depends(get_db)):
    # Проверка доступных экземпляров книги
    book = await db.get(Book, loan.book_id)
    if not book or book.available_copies < 1:
        raise HTTPException(status_code=400, detail="Book is not available")

    # Проверка лимита активных займов у читателя
    active_loans_query = select(Loan).where(Loan.reader_id == loan.reader_id, Loan.return_date == None)
    result = await db.execute(active_loans_query)
    active_loans = result.scalars().all()
    if len(active_loans) >= 5:
        raise HTTPException(status_code=400, detail="Reader has reached the maximum number of active loans")

    # Проверка существования читателя
    reader = await db.get(Reader, loan.reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    # Создание займа
    new_loan = Loan(
        book_id=loan.book_id,
        reader_id=loan.reader_id,
        loan_date=date.today(),
        return_date=None,
    )
    book.available_copies -= 1
    db.add(new_loan)
    await db.commit()
    await db.refresh(new_loan)

    # Установка предполагаемой даты возврата книги через 14 дней
    due_date = date.today() + timedelta(days=14)
    new_loan.return_date = due_date

    await db.commit()
    await db.refresh(new_loan)

    return new_loan

@router.post("/{loan_id}/return", response_model=LoanRead)
async def return_loan(loan_id: int, db: AsyncSession = Depends(get_db)):
    loan = await db.get(Loan, loan_id)
    if not loan or loan.return_date is not None:
        raise HTTPException(status_code=400, detail="Invalid loan ID or loan already returned")

    # Возврат книги
    loan.return_date = date.today()
    book = await db.get(Book, loan.book_id)
    if book:
        book.available_copies += 1

    await db.commit()
    await db.refresh(loan)
    return loan

@router.get("/", response_model=List[LoanRead])
async def get_loans(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Loan).offset(skip).limit(limit))
    loans = result.scalars().all()
    return loans

