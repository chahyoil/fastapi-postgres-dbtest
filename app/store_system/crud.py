from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.store_system import models, schemas
from app import CRUDBase

class CRUDStore(CRUDBase[models.Store, schemas.StoreCreate, schemas.StoreCreate]):
    def get_by_location(self, db: Session, location: str, skip: int = 0, limit: int = 100) -> List[models.Store]:
        return db.query(self.model).filter(func.lower(self.model.location) == func.lower(location)).offset(skip).limit(limit).all()

class CRUDStoreInspection(CRUDBase[models.StoreInspection, schemas.StoreInspectionCreate, schemas.StoreInspectionCreate]):
    def get_by_store_id(self, db: Session, store_id: int, skip: int = 0, limit: int = 100) -> List[models.StoreInspection]:
        return db.query(self.model).filter(self.model.store_id == store_id).offset(skip).limit(limit).all()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.StoreInspection]:
        return db.query(self.model).filter(self.model.inspection_date.between(start_date, end_date)).offset(skip).limit(limit).all()

class CRUDProduct(CRUDBase[models.Product, schemas.ProductCreate, schemas.ProductCreate]):
    def get_by_price_range(self, db: Session, min_price: float, max_price: float, skip: int = 0, limit: int = 100) -> List[models.Product]:
        return db.query(self.model).filter(self.model.price.between(min_price, max_price)).offset(skip).limit(limit).all()

class CRUDProductArrival(CRUDBase[models.ProductArrival, schemas.ProductArrivalCreate, schemas.ProductArrivalCreate]):
    def get_by_product_id(self, db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[models.ProductArrival]:
        return db.query(self.model).filter(self.model.product_id == product_id).offset(skip).limit(limit).all()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.ProductArrival]:
        return db.query(self.model).filter(self.model.arrival_date.between(start_date, end_date)).offset(skip).limit(limit).all()

class CRUDCustomer(CRUDBase[models.Customer, schemas.CustomerCreate, schemas.CustomerCreate]):
    def get_by_email(self, db: Session, email: str) -> Optional[models.Customer]:
        return db.query(self.model).filter(self.model.email == email).first()

class CRUDPurchase(CRUDBase[models.Purchase, schemas.PurchaseCreate, schemas.PurchaseCreate]):
    def get_by_customer_id(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
        return db.query(self.model).filter(self.model.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_by_product_id(self, db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
        return db.query(self.model).filter(self.model.product_id == product_id).offset(skip).limit(limit).all()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
        return db.query(self.model).filter(self.model.purchase_date.between(start_date, end_date)).offset(skip).limit(limit).all()

store = CRUDStore(models.Store)
store_inspection = CRUDStoreInspection(models.StoreInspection)
product = CRUDProduct(models.Product)
product_arrival = CRUDProductArrival(models.ProductArrival)
customer = CRUDCustomer(models.Customer)
purchase = CRUDPurchase(models.Purchase)

# Convenience functions
def get_store_by_location(db: Session, location: str, skip: int = 0, limit: int = 100) -> List[models.Store]:
    return store.get_by_location(db, location=location, skip=skip, limit=limit)

def get_store_inspections_by_store(db: Session, store_id: int, skip: int = 0, limit: int = 100) -> List[models.StoreInspection]:
    return store_inspection.get_by_store_id(db, store_id=store_id, skip=skip, limit=limit)

def get_store_inspections_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.StoreInspection]:
    return store_inspection.get_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

def get_products_by_price_range(db: Session, min_price: float, max_price: float, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return product.get_by_price_range(db, min_price=min_price, max_price=max_price, skip=skip, limit=limit)

def get_product_arrivals_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[models.ProductArrival]:
    return product_arrival.get_by_product_id(db, product_id=product_id, skip=skip, limit=limit)

def get_product_arrivals_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.ProductArrival]:
    return product_arrival.get_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
    return customer.get_by_email(db, email=email)

def get_purchases_by_customer(db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
    return purchase.get_by_customer_id(db, customer_id=customer_id, skip=skip, limit=limit)

def get_purchases_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
    return purchase.get_by_product_id(db, product_id=product_id, skip=skip, limit=limit)

def get_purchases_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[models.Purchase]:
    return purchase.get_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)