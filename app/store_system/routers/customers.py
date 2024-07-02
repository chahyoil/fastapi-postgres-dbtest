from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        return crud.customer.create(db=db, obj_in=customer)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")

@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.customer.get(db=db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = crud.customer.get(db=db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.customer.update(db=db, db_obj=db_customer, obj_in=customer)

@router.delete("/{customer_id}", response_model=schemas.Customer)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.customer.get(db=db, id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.customer.delete(db=db, id=customer_id)

@router.get("/", response_model=List[schemas.Customer])
def read_customers(
    email: str = Query(None, description="Filter customers by email"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if email:
        customer = crud.get_customer_by_email(db, email=email)
        return [customer] if customer else []
    else:
        return crud.customer.get_multi(db, skip=skip, limit=limit)