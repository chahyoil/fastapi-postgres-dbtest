import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.main import app
from app.store_system import crud, schemas
from app.core.database import get_db, Base, engine
from app.store_system.tests.factories import CustomerFactory, ProductFactory, PurchaseFactory

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


# 기존의 fixture들은 그대로 유지

@pytest.fixture(scope="function")
def test_customer(test_client):
    customer = CustomerFactory.build()
    response = test_client.post("/store-system/customers/", json=CustomerFactory.to_dict(customer))
    return response.json()

@pytest.fixture(scope="function")
def test_product(test_client):
    product = ProductFactory.build()
    response = test_client.post("/store-system/products/", json=ProductFactory.to_dict(product))
    return response.json()

@pytest.mark.order(1)
def test_create_purchase(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    purchase_data = PurchaseFactory.to_dict(purchase)
    response = test_client.post("/store-system/purchases/", json=purchase_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == purchase_data["customer_id"]
    assert data["product_id"] == purchase_data["product_id"]
    assert data["purchase_date"] == purchase_data["purchase_date"]
    assert data["quantity"] == purchase_data["quantity"]
    assert "id" in data

@pytest.mark.order(2)
def test_read_purchase(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    purchase_data = PurchaseFactory.to_dict(purchase)
    create_response = test_client.post("/store-system/purchases/", json=purchase_data)
    created_purchase = create_response.json()

    response = test_client.get(f"/store-system/purchases/{created_purchase['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == purchase_data["customer_id"]
    assert data["product_id"] == purchase_data["product_id"]
    assert data["purchase_date"] == purchase_data["purchase_date"]
    assert data["quantity"] == purchase_data["quantity"]

@pytest.mark.order(7)
def test_update_purchase(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    purchase_data = PurchaseFactory.to_dict(purchase)
    create_response = test_client.post("/store-system/purchases/", json=purchase_data)
    created_purchase = create_response.json()

    updated_purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"],
        purchase_date=date.today() + timedelta(days=1),
        quantity=3
    )
    update_data = PurchaseFactory.to_dict(updated_purchase)
    response = test_client.put(f"/store-system/purchases/{created_purchase['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["purchase_date"] == update_data["purchase_date"]
    assert data["quantity"] == update_data["quantity"]

@pytest.mark.order(8)
def test_delete_purchase(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    purchase_data = PurchaseFactory.to_dict(purchase)
    create_response = test_client.post("/store-system/purchases/", json=purchase_data)
    created_purchase = create_response.json()

    response = test_client.delete(f"/store-system/purchases/{created_purchase['id']}")
    assert response.status_code == 200

    get_response = test_client.get(f"/store-system/purchases/{created_purchase['id']}")
    assert get_response.status_code == 404

@pytest.mark.order(3)
def test_read_purchases(test_client, test_customer, test_product):
    purchase1 = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"],
        quantity=1
    )
    purchase2 = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"],
        quantity=2
    )
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase1))
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase2))

    response = test_client.get("/store-system/purchases/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(purchase["quantity"] == 1 for purchase in data)
    assert any(purchase["quantity"] == 2 for purchase in data)

@pytest.mark.order(4)
def test_read_purchases_by_customer(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase))

    response = test_client.get(f"/store-system/purchases/?customer_id={test_customer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(purchase["customer_id"] == test_customer["id"] for purchase in data)

@pytest.mark.order(5)
def test_read_purchases_by_product(test_client, test_customer, test_product):
    purchase = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    )
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase))

    response = test_client.get(f"/store-system/purchases/?product_id={test_product['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(purchase["product_id"] == test_product["id"] for purchase in data)

@pytest.mark.order(6)
def test_read_purchases_by_date_range(test_client, test_customer, test_product):
    purchase1 = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"],
        purchase_date=date.today() - timedelta(days=5)
    )
    purchase2 = PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"],
        purchase_date=date.today()
    )
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase1))
    test_client.post("/store-system/purchases/", json=PurchaseFactory.to_dict(purchase2))

    start_date = str(date.today() - timedelta(days=3))
    end_date = str(date.today() + timedelta(days=1))
    response = test_client.get(f"/store-system/purchases/?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(start_date <= purchase["purchase_date"] <= end_date for purchase in data)

@pytest.mark.order(9)
def test_read_purchase_not_found(test_client):
    response = test_client.get("/store-system/purchases/99999")
    assert response.status_code == 404

@pytest.mark.order(10)
def test_update_purchase_not_found(test_client, test_customer, test_product):
    update_data = PurchaseFactory.to_dict(PurchaseFactory.build(
        customer_id=test_customer["id"],
        product_id=test_product["id"]
    ))
    response = test_client.put("/store-system/purchases/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.order(11)
def test_delete_purchase_not_found(test_client):
    response = test_client.delete("/store-system/purchases/99999")
    assert response.status_code == 404