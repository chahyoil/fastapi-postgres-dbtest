from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ProductArrival)
def create_product_arrival(arrival: schemas.ProductArrivalCreate, db: Session = Depends(get_db)):
    return crud.product_arrival.create(db=db, obj_in=arrival)

@router.get("/{arrival_id}", response_model=schemas.ProductArrival)
def read_product_arrival(arrival_id: int, db: Session = Depends(get_db)):
    db_arrival = crud.product_arrival.get(db=db, id=arrival_id)
    if db_arrival is None:
        raise HTTPException(status_code=404, detail="Product arrival not found")
    return db_arrival

@router.put("/{arrival_id}", response_model=schemas.ProductArrival)
def update_product_arrival(arrival_id: int, arrival: schemas.ProductArrivalCreate, db: Session = Depends(get_db)):
    db_arrival = crud.product_arrival.get(db=db, id=arrival_id)
    if db_arrival is None:
        raise HTTPException(status_code=404, detail="Product arrival not found")
    return crud.product_arrival.update(db=db, db_obj=db_arrival, obj_in=arrival)

@router.delete("/{arrival_id}", response_model=schemas.ProductArrival)
def delete_product_arrival(arrival_id: int, db: Session = Depends(get_db)):
    db_arrival = crud.product_arrival.get(db=db, id=arrival_id)
    if db_arrival is None:
        raise HTTPException(status_code=404, detail="Product arrival not found")
    return crud.product_arrival.remove(db=db, id=arrival_id)

@router.get("/", response_model=List[schemas.ProductArrival])
def read_product_arrivals(
    product_id: int = Query(None, description="Filter arrivals by product ID"),
    start_date: date = Query(None, description="Start date for date range filter"),
    end_date: date = Query(None, description="End date for date range filter"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if product_id:
        return crud.get_product_arrivals_by_product(db, product_id=product_id, skip=skip, limit=limit)
    elif start_date and end_date:
        return crud.get_product_arrivals_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    else:
        return crud.product_arrival.get_multi(db, skip=skip, limit=limit)