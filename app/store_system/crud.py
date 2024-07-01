from sqlalchemy.orm import Session
from . import models, schemas
from app import CRUDBase

class CRUDStore(CRUDBase):
    def __init__(self):
        super().__init__(models.Store)

class CRUDStoreInspection(CRUDBase):
    def __init__(self):
        super().__init__(models.StoreInspection)

class CRUDProduct(CRUDBase):
    def __init__(self):
        super().__init__(models.Product)

class CRUDProductArrival(CRUDBase):
    def __init__(self):
        super().__init__(models.ProductArrival)

class CRUDCustomer(CRUDBase):
    def __init__(self):
        super().__init__(models.Customer)

class CRUDPurchase(CRUDBase):
    def __init__(self):
        super().__init__(models.Purchase)

store = CRUDStore()
store_inspection = CRUDStoreInspection()
product = CRUDProduct()
product_arrival = CRUDProductArrival()
customer = CRUDCustomer()
purchase = CRUDPurchase()

def create_store(db: Session, store: schemas.StoreCreate):
    return store.create(db, store)

def get_store(db: Session, store_id: int):
    return store.get(db, store_id)

def create_store_inspection(db: Session, inspection: schemas.StoreInspectionCreate):
    return store_inspection.create(db, inspection)

def create_product(db: Session, product_in: schemas.ProductCreate):
    return product.create(db, product_in)

def get_product(db: Session, product_id: int):
    return product.get(db, product_id)

def create_product_arrival(db: Session, arrival: schemas.ProductArrivalCreate):
    return product_arrival.create(db, arrival)

def create_customer(db: Session, customer: schemas.CustomerCreate):
    return customer.create(db, customer)

def get_customer(db: Session, customer_id: int):
    return customer.get(db, customer_id)

def create_purchase(db: Session, purchase: schemas.PurchaseCreate):
    return purchase.create(db, purchase)