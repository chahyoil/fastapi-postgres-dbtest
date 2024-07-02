from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Store)
def create_store(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    return crud.store.create(db=db, obj_in=store)

@router.get("/{store_id}", response_model=schemas.Store)
def read_store(store_id: int, db: Session = Depends(get_db)):
    db_store = crud.store.get(db=db, id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store

@router.put("/{store_id}", response_model=schemas.Store)
def update_store(store_id: int, store: schemas.StoreCreate, db: Session = Depends(get_db)):
    db_store = crud.store.get(db=db, id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return crud.store.update(db=db, db_obj=db_store, obj_in=store)

@router.delete("/{store_id}", response_model=schemas.Store)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    db_store = crud.store.get(db=db, id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return crud.store.delete(db=db, id=store_id)

@router.get("/", response_model=List[schemas.Store])
def read_stores(
    location: str = Query(None, description="Filter stores by location"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if location:
        stores = crud.get_store_by_location(db, location=location, skip=skip, limit=limit)
    else:
        stores = crud.store.get_multi(db, skip=skip, limit=limit)
    return stores