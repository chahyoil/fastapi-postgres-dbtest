import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine
from app.store_system.tests.factories import StoreFactory, StoreInspectionFactory


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



@pytest.fixture(scope="function")
def test_store(test_client):
    store = StoreFactory.build()
    response = test_client.post("/store-system/stores/", json=StoreFactory.to_dict(store))
    return response.json()

@pytest.mark.order(1)
def test_create_store_inspection(test_client, test_store):
    inspection = StoreInspectionFactory.build(store_id=test_store["id"])
    inspection_data = StoreInspectionFactory.to_dict(inspection)
    response = test_client.post("/store-system/store-inspections/", json=inspection_data)
    assert response.status_code == 200
    data = response.json()
    assert data["store_id"] == inspection_data["store_id"]
    assert data["inspection_date"] == inspection_data["inspection_date"]
    assert data["result"] == inspection_data["result"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_store_inspection(test_client, test_store):
    inspection = StoreInspectionFactory.build(store_id=test_store["id"])
    inspection_data = StoreInspectionFactory.to_dict(inspection)
    create_response = test_client.post("/store-system/store-inspections/", json=inspection_data)
    created_inspection = create_response.json()

    response = test_client.get(f"/store-system/store-inspections/{created_inspection['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["store_id"] == inspection_data["store_id"]
    assert data["inspection_date"] == inspection_data["inspection_date"]
    assert data["result"] == inspection_data["result"]

@pytest.mark.order(6)
def test_update_store_inspection(test_client, test_store):
    inspection = StoreInspectionFactory.build(store_id=test_store["id"])
    inspection_data = StoreInspectionFactory.to_dict(inspection)
    create_response = test_client.post("/store-system/store-inspections/", json=inspection_data)
    created_inspection = create_response.json()

    updated_inspection = StoreInspectionFactory.build(
        store_id=test_store["id"],
        inspection_date=date.today() + timedelta(days=1),
        result="Failed"
    )
    update_data = StoreInspectionFactory.to_dict(updated_inspection)
    response = test_client.put(f"/store-system/store-inspections/{created_inspection['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["inspection_date"] == update_data["inspection_date"]
    assert data["result"] == update_data["result"]

@pytest.mark.order(7)
def test_delete_store_inspection(test_client, test_store):
    inspection = StoreInspectionFactory.build(store_id=test_store["id"])
    inspection_data = StoreInspectionFactory.to_dict(inspection)
    create_response = test_client.post("/store-system/store-inspections/", json=inspection_data)
    created_inspection = create_response.json()

    response = test_client.delete(f"/store-system/store-inspections/{created_inspection['id']}")
    assert response.status_code == 200

    get_response = test_client.get(f"/store-system/store-inspections/{created_inspection['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_store_inspections(test_client, test_store):
    inspection1 = StoreInspectionFactory.build(store_id=test_store["id"], result="Passed")
    inspection2 = StoreInspectionFactory.build(store_id=test_store["id"], result="Failed")
    test_client.post("/store-system/store-inspections/", json=StoreInspectionFactory.to_dict(inspection1))
    test_client.post("/store-system/store-inspections/", json=StoreInspectionFactory.to_dict(inspection2))

    response = test_client.get("/store-system/store-inspections/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(inspection["result"] == "Passed" for inspection in data)
    assert any(inspection["result"] == "Failed" for inspection in data)

@pytest.mark.order(4)
def test_read_store_inspections_by_store(test_client, test_store):
    inspection = StoreInspectionFactory.build(store_id=test_store["id"])
    test_client.post("/store-system/store-inspections/", json=StoreInspectionFactory.to_dict(inspection))

    response = test_client.get(f"/store-system/store-inspections/?store_id={test_store['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(inspection["store_id"] == test_store["id"] for inspection in data)

@pytest.mark.order(5)
def test_read_store_inspections_by_date_range(test_client, test_store):
    inspection1 = StoreInspectionFactory.build(
        store_id=test_store["id"],
        inspection_date=str(date.today() - timedelta(days=5))
    )
    inspection2 = StoreInspectionFactory.build(
        store_id=test_store["id"],
        inspection_date=str(date.today())
    )
    test_client.post("/store-system/store-inspections/", json=StoreInspectionFactory.to_dict(inspection1))
    test_client.post("/store-system/store-inspections/", json=StoreInspectionFactory.to_dict(inspection2))

    start_date = str(date.today() - timedelta(days=3))
    end_date = str(date.today() + timedelta(days=1))
    response = test_client.get(f"/store-system/store-inspections/?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(start_date <= inspection["inspection_date"] <= end_date for inspection in data)

@pytest.mark.order(8)
def test_read_store_inspection_not_found(test_client):
    response = test_client.get("/store-system/store-inspections/99999")
    assert response.status_code == 404

@pytest.mark.order(9)
def test_update_store_inspection_not_found(test_client, test_store):
    update_data = StoreInspectionFactory.to_dict(StoreInspectionFactory.build(store_id=test_store["id"]))
    response = test_client.put("/store-system/store-inspections/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.order(10)
def test_delete_store_inspection_not_found(test_client):
    response = test_client.delete("/store-system/store-inspections/99999")
    assert response.status_code == 404