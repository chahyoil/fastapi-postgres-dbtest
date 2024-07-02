from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.StoreInspection)
def create_store_inspection(inspection: schemas.StoreInspectionCreate, db: Session = Depends(get_db)):
    return crud.store_inspection.create(db=db, obj_in=inspection)

@router.get("/{inspection_id}", response_model=schemas.StoreInspection)
def read_store_inspection(inspection_id: int, db: Session = Depends(get_db)):
    db_inspection = crud.store_inspection.get(db=db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="Store inspection not found")
    return db_inspection

@router.put("/{inspection_id}", response_model=schemas.StoreInspection)
def update_store_inspection(inspection_id: int, inspection: schemas.StoreInspectionCreate, db: Session = Depends(get_db)):
    db_inspection = crud.store_inspection.get(db=db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="Store inspection not found")
    return crud.store_inspection.update(db=db, db_obj=db_inspection, obj_in=inspection)

@router.delete("/{inspection_id}", response_model=schemas.StoreInspection)
def delete_store_inspection(inspection_id: int, db: Session = Depends(get_db)):
    db_inspection = crud.store_inspection.get(db=db, id=inspection_id)
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="Store inspection not found")
    return crud.store_inspection.delete(db=db, id=inspection_id)

@router.get("/", response_model=List[schemas.StoreInspection])
def read_store_inspections(
    store_id: int = Query(None, description="Filter inspections by store ID"),
    start_date: date = Query(None, description="Start date for date range filter"),
    end_date: date = Query(None, description="End date for date range filter"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if store_id:
        return crud.get_store_inspections_by_store(db, store_id=store_id, skip=skip, limit=limit)
    elif start_date and end_date:
        return crud.get_store_inspections_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)
    else:
        return crud.store_inspection.get_multi(db, skip=skip, limit=limit)