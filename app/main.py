from fastapi import FastAPI
from app.routers import books, authors, readers, loans, genres
from app.database import init_db

app = FastAPI()

# Инициализация базы данных
@app.on_event("startup")
async def startup_event():
    await init_db()

# Регистрация роутеров
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(authors.router, prefix="/authors", tags=["Authors"])
app.include_router(readers.router, prefix="/readers", tags=["Readers"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
app.include_router(genres.router, prefix="/genres", tags=["Genres"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library API"}
