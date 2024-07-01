from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Purchase)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    return crud.purchase.create(db=db, obj_in=purchase)

@router.get("/{purchase_id}", response_model=schemas.Purchase)
def read_purchase(purchase_id: int, db: Session = Depends(get_db)):
    db_purchase = crud.purchase.get(db=db, id=purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return db_purchase

@router.put("/{purchase_id}", response_model=schemas.Purchase)
def update_purchase(purchase_id: int, purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    db_purchase = crud.purchase.get(db=db, id=purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return crud.purchase.update(db=db, db_obj=db_purchase, obj_in=purchase)

@router.delete("/{purchase_id}", response_model=schemas.Purchase)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    db_purchase = crud.purchase.get(db=db, id=purchase_id)
    if db_purchase is None:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return crud.purchase.remove(db=db, id=purchase_id)

@router.get("/", response_model=List[schemas.Purchase])
def read_purchases(
    customer_id: int = Query(None, description="Filter purchases by customer ID"),
    product_id: int = Query(None, description="Filter purchases by product ID"),
    start_date: date = Query(None, description="Start date for date range filter"),
    end_date: date = Query(None, description="End date for date range filter"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if customer_id:
        return crud.get_purchases_by_customer(db, customer_id=customer_id, skip=skip, limit=limit)
    elif product_id:
        return crud.get_purchases_by_product(db, product_id=product_id, skip=skip, limit=limit)
    elif start_date and end_date:
        return crud.get_purchases_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    else:
        return crud.purchase.get_multi(db, skip=skip, limit=limit)