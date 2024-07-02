from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.store_system import crud, schemas
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.product.create(db=db, obj_in=product)

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.product.get(db=db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.product.get(db=db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product.update(db=db, db_obj=db_product, obj_in=product)

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.product.get(db=db, id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product.delete(db=db, id=product_id)

@router.get("/", response_model=List[schemas.Product])
def read_products(
    min_price: float = Query(None, description="Minimum price for filtering products"),
    max_price: float = Query(None, description="Maximum price for filtering products"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if min_price is not None and max_price is not None:
        products = crud.get_products_by_price_range(db, min_price=min_price, max_price=max_price, skip=skip, limit=limit)
    else:
        products = crud.product.get_multi(db, skip=skip, limit=limit)
    return products