import pytest
from datetime import date
from app.models import Reader, Loan, Book
from app.database import SessionLocal
from sqlalchemy.future import select


# Фикстура для сессии базы данных
@pytest.fixture
async def db_session():
    async with SessionLocal() as session:
        yield session


# Тест на создание читателя (Reader)
@pytest.mark.asyncio
async def test_create_reader(db_session):
    # Создаем нового читателя
    reader = Reader(
        name="Test Reader",
        email="reader@example.com",
        hashed_password="fakehashedpassword"
    )
    db_session.add(reader)
    await db_session.commit()

    # Проверяем, что читатель был добавлен в базу
    result = await db_session.execute(select(Reader).filter(Reader.email == "reader@example.com"))
    reader_from_db = result.scalar_one_or_none()

    assert reader_from_db is not None
    assert reader_from_db.name == "Test Reader"
    assert reader_from_db.email == "reader@example.com"
    assert reader_from_db.hashed_password == "fakehashedpassword"


# Тест на уникальность email читателя
@pytest.mark.asyncio
async def test_reader_email_unique(db_session):
    # Создаем двух читателей с одинаковыми email
    reader1 = Reader(
        name="Reader 1",
        email="uniqueemail@example.com",
        hashed_password="fakehashedpassword1"
    )
    reader2 = Reader(
        name="Reader 2",
        email="uniqueemail@example.com",  # тот же email
        hashed_password="fakehashedpassword2"
    )

    db_session.add(reader1)
    try:
        await db_session.commit()
    except Exception:
        await db_session.rollback()

    db_session.add(reader2)
    try:
        await db_session.commit()  # Ожидаем, что будет ошибка из-за уникальности email
        assert False, "Should raise an error due to non-unique email"
    except Exception as e:
        assert "unique constraint" in str(e)  # Проверяем, что ошибка связана с нарушением уникальности email


# Тест на создание читателя без обязательного поля (например, email)
@pytest.mark.asyncio
async def test_create_reader_without_required_field(db_session):
    # Попытка создать читателя без обязательного поля email
    reader = Reader(
        name="Reader Without Email",
        hashed_password="fakehashedpassword"
    )

    db_session.add(reader)
    try:
        await db_session.commit()
        assert False, "Should raise an error due to missing required field (email)"
    except Exception as e:
        assert "email" in str(e)  # Проверяем, что ошибка связана с отсутствием email


# Тест на создание читателя и связь с займом (Loan)
@pytest.mark.asyncio
async def test_reader_loan_relationship(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Book for Loan",
        description="A book for testing loans",
        publication_date=date(2023, 1, 1),
        available_copies=5
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем читателя
    reader = Reader(
        name="Reader with Loan",
        email="readerloan@example.com",
        hashed_password="fakehashedpassword"
    )
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ для читателя
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 6, 1),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Проверяем, что читатель имеет связанные займы
    result = await db_session.execute(select(Reader).filter(Reader.email == "readerloan@example.com"))
    reader_from_db = result.scalar_one_or_none()

    assert reader_from_db is not None
    assert len(reader_from_db.loans) == 1
    assert reader_from_db.loans[0].book_id == book.id


# Тест на удаление читателя с удалением его займов (с использованием каскадных удалений)
@pytest.mark.asyncio
async def test_delete_reader_with_loans(db_session):
    # Создаем фейковую книгу
    book = Book(
        title="Book to Return",
        description="Book for testing delete",
        publication_date=date(2023, 1, 1),
        available_copies=3
    )
    db_session.add(book)
    await db_session.commit()

    # Создаем читателя
    reader = Reader(
        name="Reader for Deletion",
        email="readertodelete@example.com",
        hashed_password="fakehashedpassword"
    )
    db_session.add(reader)
    await db_session.commit()

    # Создаем займ для читателя
    loan = Loan(
        book_id=book.id,
        reader_id=reader.id,
        loan_date=date(2023, 6, 1),
        return_date=None
    )
    db_session.add(loan)
    await db_session.commit()

    # Удаляем читателя
    await db_session.delete(reader)
    await db_session.commit()

    # Проверяем, что читатель и его займы были удалены
    result = await db_session.execute(select(Reader).filter(Reader.email == "readertodelete@example.com"))
    reader_from_db = result.scalar_one_or_none()

    assert reader_from_db is None  # Читатель должен быть удален

    # Проверяем, что займ также удален
    result = await db_session.execute(select(Loan).filter(Loan.reader_id == reader.id))
    loan_from_db = result.scalar_one_or_none()

    assert loan_from_db is None  # Займ должен быть удален с удалением читателя


# Тест на создание читателя с хешированным паролем
@pytest.mark.asyncio
async def test_reader_password_hash(db_session):
    # Создаем нового читателя с хешированным паролем
    reader = Reader(
        name="Reader with Password Hash",
        email="readerpassword@example.com",
        hashed_password="fakehashedpassword"
    )
    db_session.add(reader)
    await db_session.commit()

    # Проверяем, что хешированный пароль сохранен в базе
    result = await db_session.execute(select(Reader).filter(Reader.email == "readerpassword@example.com"))
    reader_from_db = result.scalar_one_or_none()

    assert reader_from_db is not None
    assert reader_from_db.hashed_password == "fakehashedpassword"
