import factory
from factory.faker import Faker
from app.store_system import models

class CustomerFactory(factory.Factory):
    class Meta:
        model = models.Customer

    name = Faker('name')
    email = Faker('email')

class ProductFactory(factory.Factory):
    class Meta:
        model = models.Product

    name = Faker('word')
    price = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)

class StoreFactory(factory.Factory):
    class Meta:
        model = models.Store

    name = Faker('company')
    location = Faker('address')

class PurchaseFactory(factory.Factory):
    class Meta:
        model = models.Purchase

    customer = factory.SubFactory(CustomerFactory)
    product = factory.SubFactory(ProductFactory)
    purchase_date = Faker('date_this_year')
    quantity = Faker('random_int', min=1, max=10)