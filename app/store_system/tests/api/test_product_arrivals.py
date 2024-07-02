import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine

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
    product_data = {"name": "Test Product", "price": 9.99}
    response = test_client.post("/store-system/products/", json=product_data)
    return response.json()

@pytest.mark.order(1)
def test_create_product_arrival(test_client, test_product):
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 100
    }
    response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == arrival_data["product_id"]
    assert data["arrival_date"] == arrival_data["arrival_date"]
    assert data["quantity"] == arrival_data["quantity"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_product_arrival(test_client, test_product):
    # First, create a product arrival
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 50
    }
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    # Then, read the created product arrival
    response = test_client.get(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == arrival_data["product_id"]
    assert data["arrival_date"] == arrival_data["arrival_date"]
    assert data["quantity"] == arrival_data["quantity"]

@pytest.mark.order(6)
def test_update_product_arrival(test_client, test_product):
    # First, create a product arrival
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 75
    }
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    # Then, update the product arrival
    update_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today() + timedelta(days=1)),
        "quantity": 80
    }
    response = test_client.put(f"/store-system/product-arrivals/{created_arrival['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["arrival_date"] == update_data["arrival_date"]
    assert data["quantity"] == update_data["quantity"]

@pytest.mark.order(7)
def test_delete_product_arrival(test_client, test_product):
    # First, create a product arrival
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 25
    }
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    # Then, delete the product arrival
    response = test_client.delete(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert response.status_code == 200

    # Verify that the product arrival has been deleted
    get_response = test_client.get(f"/store-system/product-arrivals/{created_arrival['id']}")
    assert get_response.status_code == 404


@pytest.mark.order(3)
def test_read_product_arrivals(test_client, test_product):
    # Create multiple product arrivals
    arrival_data1 = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 30
    }
    arrival_data2 = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today() + timedelta(days=1)),
        "quantity": 40
    }
    test_client.post("/store-system/product-arrivals/", json=arrival_data1)
    test_client.post("/store-system/product-arrivals/", json=arrival_data2)

    # Read all product arrivals
    response = test_client.get("/store-system/product-arrivals/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(arrival["quantity"] == 30 for arrival in data)
    assert any(arrival["quantity"] == 40 for arrival in data)

@pytest.mark.order(4)
def test_read_product_arrivals_by_product(test_client, test_product):
    # Create a product arrival for the test product
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 60
    }
    test_client.post("/store-system/product-arrivals/", json=arrival_data)

    # Read product arrivals for the specific product
    response = test_client.get(f"/store-system/product-arrivals/?product_id={test_product['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(arrival["product_id"] == test_product["id"] for arrival in data)


@pytest.mark.order(5)
def test_read_product_arrivals_by_date_range(test_client, test_product):
    # Create product arrivals with different dates
    arrival_data1 = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today() - timedelta(days=5)),
        "quantity": 70
    }
    arrival_data2 = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 80
    }
    test_client.post("/store-system/product-arrivals/", json=arrival_data1)
    test_client.post("/store-system/product-arrivals/", json=arrival_data2)

    # Read product arrivals within a date range
    start_date = str(date.today() - timedelta(days=3))
    end_date = str(date.today() + timedelta(days=1))
    response = test_client.get(f"/store-system/product-arrivals/?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(start_date <= arrival["arrival_date"] <= end_date for arrival in data)


@pytest.mark.order(8)
def test_read_product_arrival_not_found(test_client):
    response = test_client.get("/store-system/product-arrivals/99999")  # Assuming this ID doesn't exist
    assert response.status_code == 404

@pytest.mark.order(9)
def test_update_product_arrival_not_found(test_client, test_product):
    update_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 90
    }
    response = test_client.put("/store-system/product-arrivals/99999",
                               json=update_data)  # Assuming this ID doesn't exist
    assert response.status_code == 404

@pytest.mark.order(10)
def test_delete_product_arrival_not_found(test_client):
    response = test_client.delete("/store-system/product-arrivals/99999")  # Assuming this ID doesn't exist
    assert response.status_code == 404

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
    # First, create a valid product arrival
    arrival_data = {
        "product_id": test_product["id"],
        "arrival_date": str(date.today()),
        "quantity": 100
    }
    create_response = test_client.post("/store-system/product-arrivals/", json=arrival_data)
    created_arrival = create_response.json()

    # Then, try to update with invalid data
    invalid_update_data = {
        "product_id": test_product["id"],
        "arrival_date": "invalid_date",
        "quantity": "not a number"
    }
    response = test_client.put(f"/store-system/product-arrivals/{created_arrival['id']}", json=invalid_update_data)
    assert response.status_code == 422  # Unprocessable Entity