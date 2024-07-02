import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
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

@pytest.mark.order(1)
def test_create_customer(test_client):
    customer_data = {"name": "John Doe", "email": "john@example.com"}
    response = test_client.post("/store-system/customers/", json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_customer(test_client):
    # First, create a customer
    customer_data = {"name": "Jane Doe", "email": "jane@example.com"}
    create_response = test_client.post("/store-system/customers/", json=customer_data)
    created_customer = create_response.json()

    # Then, read the created customer
    response = test_client.get(f"/store-system/customers/{created_customer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]

@pytest.mark.order(5)
def test_update_customer(test_client):
    # First, create a customer
    customer_data = {"name": "Bob Smith", "email": "bob@example.com"}
    create_response = test_client.post("/store-system/customers/", json=customer_data)
    created_customer = create_response.json()

    # Then, update the customer
    update_data = {"name": "Robert Smith", "email": "robert@example.com"}
    response = test_client.put(f"/store-system/customers/{created_customer['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]

@pytest.mark.order(6)
def test_delete_customer(test_client):
    # First, create a customer
    customer_data = {"name": "Alice Johnson", "email": "alice@example.com"}
    create_response = test_client.post("/store-system/customers/", json=customer_data)
    created_customer = create_response.json()

    # Then, delete the customer
    response = test_client.delete(f"/store-system/customers/{created_customer['id']}")
    assert response.status_code == 200

    # Verify that the customer has been deleted
    get_response = test_client.get(f"/store-system/customers/{created_customer['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_customers(test_client):
    # Create multiple customers
    customer_data1 = {"name": "Customer 1", "email": "customer1@example.com"}
    customer_data2 = {"name": "Customer 2", "email": "customer2@example.com"}
    test_client.post("/store-system/customers/", json=customer_data1)
    test_client.post("/store-system/customers/", json=customer_data2)

    # Read all customers
    response = test_client.get("/store-system/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(customer["name"] == "Customer 1" for customer in data)
    assert any(customer["name"] == "Customer 2" for customer in data)


@pytest.mark.order(4)
def test_read_customer_by_email(test_client):
    # Create a customer
    customer_data = {"name": "Email Test", "email": "emailtest@example.com"}
    test_client.post("/store-system/customers/", json=customer_data)

    # Read customer by email
    response = test_client.get("/store-system/customers/?email=emailtest@example.com")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == customer_data["name"]
    assert data[0]["email"] == customer_data["email"]

@pytest.mark.order(7)
def test_read_customer_not_found(test_client):
    response = test_client.get("/store-system/customers/99999")  # Assuming this ID doesn't exist
    assert response.status_code == 404

@pytest.mark.order(8)
def test_update_customer_not_found(test_client):
    update_data = {"name": "Not Found", "email": "notfound@example.com"}
    response = test_client.put("/store-system/customers/99999", json=update_data)  # Assuming this ID doesn't exist
    assert response.status_code == 404

@pytest.mark.order(9)
def test_delete_customer_not_found(test_client):
    response = test_client.delete("/store-system/customers/99999")  # Assuming this ID doesn't exist
    assert response.status_code == 404

@pytest.mark.order(10)
def test_create_customer_invalid_data(test_client):
    invalid_customer_data = {"name": "Invalid", "email": "not-an-email"}
    response = test_client.post("/store-system/customers/", json=invalid_customer_data)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.order(11)
def test_create_customer_duplicate_email(test_client):
    # First, create a customer
    customer_data = {"name": "Original", "email": "duplicate@example.com"}
    test_client.post("/store-system/customers/", json=customer_data)

    # Try to create another customer with the same email
    duplicate_data = {"name": "Duplicate", "email": "duplicate@example.com"}
    response = test_client.post("/store-system/customers/", json=duplicate_data)
    assert response.status_code == 400  # Bad Request

@pytest.mark.order(12)
def test_read_customers_with_pagination(test_client):
    # Create multiple customers
    for i in range(15):
        customer_data = {"name": f"Pagination Customer {i}", "email": f"pagination{i}@example.com"}
        test_client.post("/store-system/customers/", json=customer_data)

    # Read customers with pagination
    limit = 10
    skip = 5
    response = test_client.get(f"/store-system/customers/?skip={skip}&limit={limit}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == limit
    assert all("Pagination Customer" in customer["name"] for customer in data)