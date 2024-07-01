from fastapi import FastAPI, Depends
from app.core.database import engine, get_db
from sqlalchemy.orm import Session
from app.store_system import models as store_models
from app.parking_system import models as parking_models
from loguru import logger
app = FastAPI()

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