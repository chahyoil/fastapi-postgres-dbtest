import factory
from factory.faker import Faker
from app.store_system import models
from app.core.database import SessionLocal

class CustomerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Customer
        sqlalchemy_session = SessionLocal()

    name = Faker('name')
    email = Faker('email')

class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Product
        sqlalchemy_session = SessionLocal()

    name = Faker('word')
    price = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)

class StoreFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Store
        sqlalchemy_session = SessionLocal()

    name = Faker('company')
    location = Faker('address')

class PurchaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Purchase
        sqlalchemy_session = SessionLocal()

    customer = factory.SubFactory(CustomerFactory)
    product = factory.SubFactory(ProductFactory)
    purchase_date = Faker('date_this_year')
    quantity = Faker('random_int', min=1, max=10)
