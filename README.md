## Описание
API для управления библиотечным каталогом. Система поддерживает управление книгами, авторами, читателями и выдачей книг.

## Функционал
- CRUD для книг, авторов, жанров.
- Выдача и возврат книг с учетом лимитов.
- Пагинация и фильтрация.
- Аутентификация через JWT.

## Установка
1. Клонируйте репозиторий.
```bash
git clone <repository-url>
cd lib_api
```
2. Создайте виртуальное окружение и установите зависимости.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Настройте переменные окружения для базы данных.
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/library_db
```
4. Примените миграции.
```bash
alembic upgrade head
```
5. Запустите сервер.
```bash
uvicorn app.main:app --reload
```

## Тестирование
Для запуска тестов выполните:
```bash
pytest
```

## Эндпоинты
- `GET /` - Проверка доступности API.
- `POST /authors/` - Добавление автора.
- `GET /authors/` - Получение списка авторов.

## Лицензия
MIT