from fastapi import APIRouter
from .routers import stores, store_inspections, products, product_arrivals, customers, purchases

def include_routers():
    router = APIRouter()
    router.include_router(stores.router, prefix="/stores", tags=["stores"])
    router.include_router(store_inspections.router, prefix="/store-inspections", tags=["store inspections"])
    router.include_router(products.router, prefix="/products", tags=["products"])
    router.include_router(product_arrivals.router, prefix="/product-arrivals", tags=["product arrivals"])
    router.include_router(customers.router, prefix="/customers", tags=["customers"])
    router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
    return router