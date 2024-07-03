import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine
from app.store_system.tests.factories import ProductFactory

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
def test_create_product(test_client):
    product = ProductFactory.build()
    product_data = ProductFactory.to_dict(product)
    response = test_client.post("/store-system/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_product(test_client):
    product = ProductFactory.build()
    product_data = ProductFactory.to_dict(product)
    create_response = test_client.post("/store-system/products/", json=product_data)
    created_product = create_response.json()

    response = test_client.get(f"/store-system/products/{created_product['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]

@pytest.mark.order(5)
def test_update_product(test_client):
    product = ProductFactory.build()
    product_data = ProductFactory.to_dict(product)
    create_response = test_client.post("/store-system/products/", json=product_data)
    created_product = create_response.json()

    updated_product = ProductFactory.build()
    update_data = ProductFactory.to_dict(updated_product)
    response = test_client.put(f"/store-system/products/{created_product['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]

@pytest.mark.order(6)
def test_delete_product(test_client):
    product = ProductFactory.build()
    product_data = ProductFactory.to_dict(product)
    create_response = test_client.post("/store-system/products/", json=product_data)
    created_product = create_response.json()

    response = test_client.delete(f"/store-system/products/{created_product['id']}")
    assert response.status_code == 200

    get_response = test_client.get(f"/store-system/products/{created_product['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_products(test_client):
    product1 = ProductFactory.build()
    product2 = ProductFactory.build()
    test_client.post("/store-system/products/", json=ProductFactory.to_dict(product1))
    test_client.post("/store-system/products/", json=ProductFactory.to_dict(product2))

    response = test_client.get("/store-system/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(product["name"] == product1.name for product in data)
    assert any(product["name"] == product2.name for product in data)

@pytest.mark.order(4)
def test_read_products_by_price_range(test_client):
    cheap_product = ProductFactory.build(price=5.99)
    expensive_product = ProductFactory.build(price=99.99)
    test_client.post("/store-system/products/", json=ProductFactory.to_dict(cheap_product))
    test_client.post("/store-system/products/", json=ProductFactory.to_dict(expensive_product))

    min_price = 10.00
    max_price = 100.00
    response = test_client.get(f"/store-system/products/?min_price={min_price}&max_price={max_price}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(min_price <= product["price"] <= max_price for product in data)

@pytest.mark.order(7)
def test_read_product_not_found(test_client):
    response = test_client.get("/store-system/products/99999")
    assert response.status_code == 404

@pytest.mark.order(8)
def test_update_product_not_found(test_client):
    update_data = ProductFactory.to_dict(ProductFactory.build())
    response = test_client.put("/store-system/products/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.order(9)
def test_delete_product_not_found(test_client):
    response = test_client.delete("/store-system/products/99999")
    assert response.status_code == 404

@pytest.mark.order(10)
def test_create_product_invalid_data(test_client):
    invalid_product_data = {"name": "Invalid Product", "price": "not a number"}
    response = test_client.post("/store-system/products/", json=invalid_product_data)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.order(11)
def test_update_product_invalid_data(test_client):
    product = ProductFactory.build()
    product_data = ProductFactory.to_dict(product)
    create_response = test_client.post("/store-system/products/", json=product_data)
    created_product = create_response.json()

    invalid_update_data = {"name": "Invalid Update", "price": "not a number"}
    response = test_client.put(f"/store-system/products/{created_product['id']}", json=invalid_update_data)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.order(12)
def test_read_products_with_pagination(test_client):
    for _ in range(15):
        product = ProductFactory.build()
        test_client.post("/store-system/products/", json=ProductFactory.to_dict(product))

    limit = 10
    skip = 5
    response = test_client.get(f"/store-system/products/?skip={skip}&limit={limit}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == limit