import factory
from factory.faker import Faker
from app.store_system import models
from datetime import date


class CustomerFactory(factory.Factory):
    class Meta:
        model = models.Customer

    name = Faker('name')
    email = Faker('email')

    @classmethod
    def to_dict(cls, customer):
        return {
            "name": customer.name,
            "email": customer.email
        }

class ProductFactory(factory.Factory):
    class Meta:
        model = models.Product

    name = Faker('word')
    price = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)

    @classmethod
    def to_dict(cls, product):
        return {
            "name": product.name,
            "price": float(product.price)  # Ensure price is a float
        }

class StoreFactory(factory.Factory):
    class Meta:
        model = models.Store

    name = Faker('company')
    location = Faker('address')

    @classmethod
    def to_dict(cls, store):
        return {
            "name": store.name,
            "location": store.location
        }

class PurchaseFactory(factory.Factory):
    class Meta:
        model = models.Purchase

    customer_id = factory.LazyAttribute(lambda _: CustomerFactory().id)
    product_id = factory.LazyAttribute(lambda _: ProductFactory().id)
    purchase_date = factory.LazyFunction(date.today)
    quantity = factory.Faker('random_int', min=1, max=10)

    @classmethod
    def to_dict(cls, purchase):
        return {
            "customer_id": purchase.customer_id,
            "product_id": purchase.product_id,
            "purchase_date": purchase.purchase_date.isoformat(),
            "quantity": purchase.quantity
        }

class ProductArrivalFactory(factory.Factory):
    class Meta:
        model = models.ProductArrival

    product_id = factory.LazyAttribute(lambda _: ProductFactory().id)
    arrival_date = factory.LazyFunction(date.today)
    quantity = factory.Faker('random_int', min=1, max=1000)

    @classmethod
    def to_dict(cls, product_arrival):
        return {
            "product_id": product_arrival.product_id,
            "arrival_date": product_arrival.arrival_date.isoformat() if isinstance(product_arrival.arrival_date, date) else product_arrival.arrival_date,
            "quantity": product_arrival.quantity
        }

class StoreInspectionFactory(factory.Factory):
    class Meta:
        model = models.StoreInspection

    store_id = factory.LazyAttribute(lambda _: StoreFactory().id)
    inspection_date = factory.LazyFunction(date.today)
    result = factory.Faker('random_element', elements=('Passed', 'Failed', 'Needs Improvement'))

    @classmethod
    def to_dict(cls, store_inspection):
        return {
            "store_id": store_inspection.store_id,
            "inspection_date": store_inspection.inspection_date.isoformat() if isinstance(store_inspection.inspection_date, date) else store_inspection.inspection_date,
            "result": store_inspection.result
        }