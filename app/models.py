from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Связь книги и жанра
book_genre = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    publication_date = Column(Date, nullable=False)
    available_copies = Column(Integer, default=0)

    authors = relationship("Author", back_populates="books")
    genres = relationship("Genre", secondary=book_genre, back_populates="books")

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    biography = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)

    books = relationship("Book", back_populates="authors")

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    books = relationship("Book", secondary=book_genre, back_populates="genres")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    reader_id = Column(Integer, ForeignKey("readers.id"))
    loan_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)

    book = relationship("Book")
    reader = relationship("Reader")

class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    loans = relationship("Loan", back_populates="reader")
