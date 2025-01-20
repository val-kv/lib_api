import pytest
from datetime import date
from app.models import Loan, Book, Reader
from app.database import SessionLocal
from sqlalchemy.future import select


# Фикстура для сессии базы данных
@pytest.fixture
async def db_session():
    async with SessionLocal() as session:
        yield session


# Тест на создание займа (Loan)
@pytest.mark.asyncio
async def test_create_loan(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Test Book",
        description="A book for testing",
        publication_date=date(2022, 1, 1),
        available_copies=10
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем фейкового читателя
    reader = Reader(email="testreader@example.com", hashed_password="fakehashed")
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 5, 15),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Проверяем, что займ был добавлен
    result = await db_session.execute(select(Loan).filter(Loan.book_id == book.id))
    loan_from_db = result.scalar_one_or_none()

    assert loan_from_db is not None
    assert loan_from_db.book_id == book.id
    assert loan_from_db.reader_id == reader.id
    assert loan_from_db.loan_date == date(2023, 5, 15)
    assert loan_from_db.return_date is None


# Тест на связь займа с книгой
@pytest.mark.asyncio
async def test_loan_book_relationship(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Book with Loan",
        description="Book linked to a loan",
        publication_date=date(2022, 1, 1),
        available_copies=5
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем фейкового читателя
    reader = Reader(email="reader@example.com", hashed_password="fakehashed")
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ, связанный с книгой
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 5, 20),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Проверяем связь
    result = await db_session.execute(select(Loan).filter(Loan.book_id == book.id))
    loan_from_db = result.scalar_one_or_none()

    assert loan_from_db is not None
    assert loan_from_db.book is not None
    assert loan_from_db.book.title == "Book with Loan"


# Тест на связь займа с читателем
@pytest.mark.asyncio
async def test_loan_reader_relationship(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Another Book with Loan",
        description="Another book linked to a loan",
        publication_date=date(2022, 2, 1),
        available_copies=8
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем фейкового читателя
    reader = Reader(email="reader2@example.com", hashed_password="fakehashed")
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ, связанный с читателем
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 5, 25),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Проверяем связь
    result = await db_session.execute(select(Loan).filter(Loan.reader_id == reader.id))
    loan_from_db = result.scalar_one_or_none()

    assert loan_from_db is not None
    assert loan_from_db.reader is not None
    assert loan_from_db.reader.email == "reader2@example.com"


# Тест на обновление даты возврата
@pytest.mark.asyncio
async def test_update_return_date(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Book to Return",
        description="Book for testing return date",
        publication_date=date(2023, 1, 1),
        available_copies=4
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем фейкового читателя
    reader = Reader(email="reader3@example.com", hashed_password="fakehashed")
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 6, 1),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Обновляем дату возврата
    loan.return_date = date(2023, 6, 15)
    await db_session.commit()

    # Проверяем, что дата возврата была обновлена
    result = await db_session.execute(select(Loan).filter(Loan.book_id == book.id))
    loan_from_db = result.scalar_one_or_none()

    assert loan_from_db is not None
    assert loan_from_db.return_date == date(2023, 6, 15)


# Тест на создание займа без обязательных полей
@pytest.mark.asyncio
async def test_create_loan_without_required_fields(db_session):
    # Попытка создать займ без обязательных полей
    loan = Loan(
        book_id=None,  # Без книги
        reader_id=None,  # Без читателя
        loan_date=None  # Без даты займа
    )

    db_session.add(loan)
    try:
        await db_session.commit()
        assert False, "Should raise an error due to missing required fields"
    except Exception as e:
        assert "book_id" in str(e) or "reader_id" in str(e) or "loan_date" in str(e)
