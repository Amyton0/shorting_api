import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db, BaseModel
from main import app
from models.urls import UrlsModel


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with SessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def drop():
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)

    asyncio.run(create())
    yield
    asyncio.run(drop())


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost"
    ) as ac:
        yield ac


pytestmark = pytest.mark.asyncio


async def test_shorten(client):
    response = await client.post("/shorten", params={"url": "https://example.com"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert isinstance(response.json()["id"], int)


async def test_redirect(client):
    async with SessionLocal() as db:
        new_url = UrlsModel(url="https://google.com")
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)

        response = await client.get(f"/{new_url.id}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://google.com"


async def test_invalid_id(client):
    response = await client.get("/999")
    assert response.status_code == 404


async def test_stats(client):
    async with SessionLocal() as db:
        new_url = UrlsModel(url="https://google.com")
        db.add(new_url)
        await db.commit()
        await db.refresh(new_url)

    n = 5
    for _ in range(n):
        await client.get(f"/{new_url.id}", follow_redirects=False)

    response = await client.get(f"/stats/{new_url.id}")
    assert response.status_code == 200
    assert response.json()["counter"] == n


async def test_invalid_id_stats(client):
    response = await client.get("/stats/999")
    assert response.status_code == 404


async def test_multiple_urls(client):
    urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    ids = []

    for url in urls:
        response = await client.post("/shorten", params={"url": url})
        assert response.status_code == 200
        data = response.json()
        ids.append(data["id"])

    assert len(ids) == len(set(ids))
