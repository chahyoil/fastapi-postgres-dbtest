from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from loguru import logger

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        # 데이터베이스 연결 테스트
        db.execute("SELECT 1")
        logger.info("Database connection successful")
        yield db
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    finally:
        logger.info("Database connection closed")
        db.close()