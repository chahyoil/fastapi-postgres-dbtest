# app/store_system/tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.store_system.tests.factories import CustomerFactory, ProductFactory, StoreFactory, PurchaseFactory

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cgi")

# 동기 엔진 설정
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 비동기 엔진 설정
async_engine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncTestingSessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine)


@pytest.fixture(scope="module")
def test_client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def async_test_client():
    async def override_get_db():
        async with AsyncTestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture
async def async_db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session


