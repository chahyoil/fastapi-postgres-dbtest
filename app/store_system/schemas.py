from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional

class StoreBase(BaseModel):
    name: str
    location: str

class StoreCreate(StoreBase):
    pass

class Store(StoreBase):
    id: int

    class Config:
        orm_mode = True

class StoreInspectionBase(BaseModel):
    store_id: int
    inspection_date: date
    result: str

class StoreInspectionCreate(StoreInspectionBase):
    pass

class StoreInspection(StoreInspectionBase):
    id: int

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class ProductArrivalBase(BaseModel):
    product_id: int
    arrival_date: date
    quantity: int

class ProductArrivalCreate(ProductArrivalBase):
    pass

class ProductArrival(ProductArrivalBase):
    id: int

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    name: str
    email: EmailStr  # 여기를 EmailStr로 변경

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class PurchaseBase(BaseModel):
    customer_id: int
    product_id: int
    purchase_date: date
    quantity: int

class PurchaseCreate(PurchaseBase):
    pass

class Purchase(PurchaseBase):
    id: int

    class Config:
        orm_mode = True