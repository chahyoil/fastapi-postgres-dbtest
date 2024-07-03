import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine
from app.store_system.tests.factories import StoreFactory

client = TestClient(app)

@pytest.fixture(autouse=True, scope="function")
def reset_db(test_db):
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()
    yield
    test_db.rollback()

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.order(1)
def test_create_store(test_client):
    store = StoreFactory.build()
    store_data = StoreFactory.to_dict(store)
    response = test_client.post("/store-system/stores/", json=store_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == store_data["name"]
    assert data["location"] == store_data["location"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_store(test_client):
    store = StoreFactory.build()
    store_data = StoreFactory.to_dict(store)
    create_response = test_client.post("/store-system/stores/", json=store_data)
    created_store = create_response.json()

    response = test_client.get(f"/store-system/stores/{created_store['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == store_data["name"]
    assert data["location"] == store_data["location"]

@pytest.mark.order(5)
def test_update_store(test_client):
    store = StoreFactory.build()
    store_data = StoreFactory.to_dict(store)
    create_response = test_client.post("/store-system/stores/", json=store_data)
    created_store = create_response.json()

    updated_store = StoreFactory.build()
    update_data = StoreFactory.to_dict(updated_store)
    response = test_client.put(f"/store-system/stores/{created_store['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["location"] == update_data["location"]

@pytest.mark.order(6)
def test_delete_store(test_client):
    store = StoreFactory.build()
    store_data = StoreFactory.to_dict(store)
    create_response = test_client.post("/store-system/stores/", json=store_data)
    created_store = create_response.json()

    response = test_client.delete(f"/store-system/stores/{created_store['id']}")
    assert response.status_code == 200

    get_response = test_client.get(f"/store-system/stores/{created_store['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_stores(test_client):
    store1 = StoreFactory.build()
    store2 = StoreFactory.build()
    test_client.post("/store-system/stores/", json=StoreFactory.to_dict(store1))
    test_client.post("/store-system/stores/", json=StoreFactory.to_dict(store2))

    response = test_client.get("/store-system/stores/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(store["name"] == store1.name for store in data)
    assert any(store["name"] == store2.name for store in data)

@pytest.mark.order(4)
def test_read_stores_with_filter(test_client):
    store = StoreFactory.build(location="Filter Location")
    test_client.post("/store-system/stores/", json=StoreFactory.to_dict(store))

    response = test_client.get("/store-system/stores/?location=Filter Location")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(store["location"] == "Filter Location" for store in data)

@pytest.mark.order(7)
def test_read_store_not_found(test_client):
    response = test_client.get("/store-system/stores/99999")
    assert response.status_code == 404

@pytest.mark.order(8)
def test_update_store_not_found(test_client):
    update_data = StoreFactory.to_dict(StoreFactory.build())
    response = test_client.put("/store-system/stores/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.order(9)
def test_delete_store_not_found(test_client):
    response = test_client.delete("/store-system/stores/99999")
    assert response.status_code == 404