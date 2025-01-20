import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_author():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/authors/", json={
            "name": "Author Test",
            "biography": "Biography Test",
            "birth_date": "1980-01-01"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Author Test"

@pytest.mark.asyncio
async def test_get_authors():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/authors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)