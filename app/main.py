from urllib.request import Request

from fastapi import FastAPI, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from loguru import logger
from prometheus_client import make_asgi_app
from app.core.metrics import start_timer, record_request_data
import time

from app.store_system import include_routers as include_store_routers
app = FastAPI()

app.include_router(include_store_routers(), prefix="/store-system")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Multi-System Performance Test API"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    # 데이터베이스 연결 확인
    db = next(get_db())
    db.close()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

# 데이터베이스 연결 상태를 확인하는 엔드포인트 추가
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    return {"message": "Database connection is successful"}

# 그라파나 메트릭
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = start_timer()
    response = await call_next(request)
    latency = time.time() - start_time
    record_request_data("fastapi_app", request, response, latency)
    return response
