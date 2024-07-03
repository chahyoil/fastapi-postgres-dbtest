from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from .config import settings
from loguru import logger

# 동기 엔진 설정
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 비동기 엔진 설정
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine)

Base = declarative_base()

# 동기 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        # 데이터베이스 연결 테스트
        db.execute(text("SELECT 1"))
        logger.info("Synchronous database connection successful")
        yield db
    except Exception as e:
        logger.error(f"Synchronous database connection failed: {str(e)}")
        raise
    finally:
        logger.info("Synchronous database connection closed")
        db.close()

# 비동기 세션 의존성
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            # 데이터베이스 연결 테스트
            await session.execute(text("SELECT 1"))
            logger.info("Asynchronous database connection successful")
            yield session
        except Exception as e:
            logger.error(f"Asynchronous database connection failed: {str(e)}")
            raise
        finally:
            logger.info("Asynchronous database connection closed")