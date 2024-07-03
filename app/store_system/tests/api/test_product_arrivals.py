import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine
from app.store_system.tests.factories import ProductFactory, ProductArrivalFactory

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
def test_product(test_client):
    product = ProductFactory.build()
    response = test_client.post("/store-system/products/", json=ProductFactory.to_dict(product))
    return response.json()

@pytest.mark.order(1)
def test_create_product_arrival(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival_data = ProductArrivalFactory.to_dict(arrival)
    response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == arrival_data["product_id"]
    assert data["arrival_date"] == arrival_data["arrival_date"]
    assert data["quantity"] == arrival_data["quantity"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_product_arrival(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival_data = ProductArrivalFactory.to_dict(arrival)
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    response = test_client.get(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == arrival_data["product_id"]
    assert data["arrival_date"] == arrival_data["arrival_date"]
    assert data["quantity"] == arrival_data["quantity"]

@pytest.mark.order(6)
def test_update_product_arrival(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival_data = ProductArrivalFactory.to_dict(arrival)
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    updated_arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    update_data = ProductArrivalFactory.to_dict(updated_arrival)
    response = test_client.put(f"/store-system/product-arrivals/{created_arrival['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["arrival_date"] == update_data["arrival_date"]
    assert data["quantity"] == update_data["quantity"]

@pytest.mark.order(7)
def test_delete_product_arrival(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival_data = ProductArrivalFactory.to_dict(arrival)
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    response = test_client.delete(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert response.status_code == 200

    get_response = test_client.get(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_product_arrivals(test_client, test_product):
    arrival1 = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival2 = ProductArrivalFactory.build(product_id=test_product["id"])
    test_client.post("/store-system/product-arrivals/", json=ProductArrivalFactory.to_dict(arrival1))
    test_client.post("/store-system/product-arrivals/", json=ProductArrivalFactory.to_dict(arrival2))

    response = test_client.get("/store-system/product-arrivals/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(arrival["quantity"] == arrival1.quantity for arrival in data)
    assert any(arrival["quantity"] == arrival2.quantity for arrival in data)

@pytest.mark.order(4)
def test_read_product_arrivals_by_product(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    test_client.post("/store-system/product-arrivals/", json=ProductArrivalFactory.to_dict(arrival))

    response = test_client.get(f"/store-system/product-arrivals/?product_id={test_product['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(arrival["product_id"] == test_product["id"] for arrival in data)

@pytest.mark.order(5)
def test_read_product_arrivals_by_date_range(test_client, test_product):
    arrival1 = ProductArrivalFactory.build(product_id=test_product["id"], arrival_date=date.today() - timedelta(days=5))
    arrival2 = ProductArrivalFactory.build(product_id=test_product["id"], arrival_date=date.today())
    test_client.post("/store-system/product-arrivals/", json=ProductArrivalFactory.to_dict(arrival1))
    test_client.post("/store-system/product-arrivals/", json=ProductArrivalFactory.to_dict(arrival2))

    start_date = (date.today() - timedelta(days=3)).isoformat()
    end_date = (date.today() + timedelta(days=1)).isoformat()
    response = test_client.get(f"/store-system/product-arrivals/?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(start_date <= arrival["arrival_date"] <= end_date for arrival in data)

@pytest.mark.order(11)
def test_create_product_arrival_invalid_data(test_client, test_product):
    invalid_arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": "invalid_date",
        "quantity": "not a number"
    }
    response = test_client.post("/store-system/product-arrivals/", json=invalid_arrival_data)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.order(12)
def test_update_product_arrival_invalid_data(test_client, test_product):
    arrival = ProductArrivalFactory.build(product_id=test_product["id"])
    arrival_data = ProductArrivalFactory.to_dict(arrival)
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    invalid_update_data = {
        "product_id": test_product["id"],
        "arrival_date": "invalid_date",
        "quantity": "not a number"
    }
    response = test_client.put(f"/store-system/product-arrivals/{created_arrival['id']}", json=invalid_update_data)
    assert response.status_code == 422  # Unprocessable Entity