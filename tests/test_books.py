import pytest
from datetime import date
from app.models import Book, Author, Genre
from app.database import SessionLocal
from sqlalchemy.future import select


# Фикстура для сессии базы данных
@pytest.fixture
async def db_session():
    async with SessionLocal() as session:
        yield session


# Тест создания книги
@pytest.mark.asyncio
async def test_create_book(db_session):
    # Создаем фейковую книгу
    new_book = Book(
        title="Test Book",
        description="A book for testing",
        publication_date=date(2022, 1, 1),
        available_copies=10
    )
    db_session.add(new_book)
    await db_session.commit()

    # Проверяем, что книга была добавлена
    result = await db_session.execute(select(Book).filter(Book.title == "Test Book"))
    book = result.scalar_one_or_none()

    assert book is not None
    assert book.title == "Test Book"
    assert book.description == "A book for testing"
    assert book.publication_date == date(2022, 1, 1)
    assert book.available_copies == 10


# Тест связи книги с автором
@pytest.mark.asyncio
async def test_book_author_relationship(db_session):
    # Создаем фейкового автора
    author = Author(name="Author Test")
    db_session.add(author)
    await db_session.commit()

    # Создаем книгу и связываем ее с автором
    book = Book(
        title="Book with Author",
        description="Book with an author",
        publication_date=date(2023, 5, 10),
        available_copies=5,
        authors=[author]
    )
    db_session.add(book)
    await db_session.commit()

    # Проверяем связь
    result = await db_session.execute(select(Book).filter(Book.title == "Book with Author"))
    book = result.scalar_one_or_none()

    assert book is not None
    assert len(book.authors) == 1
    assert book.authors[0].name == "Author Test"


# Тест связи книги с жанром
@pytest.mark.asyncio
async def test_book_genre_relationship(db_session):
    # Создаем фейковый жанр
    genre = Genre(name="Fiction")
    db_session.add(genre)
    await db_session.commit()

    # Создаем книгу и связываем ее с жанром
    book = Book(
        title="Book with Genre",
        description="Book with a genre",
        publication_date=date(2023, 5, 10),
        available_copies=3,
        genres=[genre]
    )
    db_session.add(book)
    await db_session.commit()

    # Проверяем связь
    result = await db_session.execute(select(Book).filter(Book.title == "Book with Genre"))
    book = result.scalar_one_or_none()

    assert book is not None
    assert len(book.genres) == 1
    assert book.genres[0].name == "Fiction"


# Тест на количество доступных копий книги
@pytest.mark.asyncio
async def test_book_available_copies(db_session):
    # Создаем книгу с доступными копиями
    new_book = Book(
        title="Book with Copies",
        description="Book with available copies",
        publication_date=date(2023, 6, 15),
        available_copies=5
    )
    db_session.add(new_book)
    await db_session.commit()

    # Проверяем количество доступных копий
    result = await db_session.execute(select(Book).filter(Book.title == "Book with Copies"))
    book = result.scalar_one_or_none()

    assert book is not None
    assert book.available_copies == 5


# Тест на создание книги без обязательного поля (publication_date)
@pytest.mark.asyncio
async def test_create_book_without_publication_date(db_session):
    # Попытка создать книгу без обязательного поля
    new_book = Book(
        title="Incomplete Book",
        description="This book is missing the publication date"
    )

    db_session.add(new_book)
    try:
        await db_session.commit()
        assert False, "Should raise an error due to missing required field"
    except Exception as e:
        assert "publication_date" in str(e)  # Проверяем, что ошибка связана с отсутствием обязательного поля
