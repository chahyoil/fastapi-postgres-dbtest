from typing import Generic, TypeVar, Type, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import contextmanager, asynccontextmanager
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @contextmanager
    def auto_commit(self, db: Session):
        try:
            yield
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        with self.auto_commit(db):
            db.add(db_obj)
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        with self.auto_commit(db):
            db.add(db_obj)
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> ModelType | None:
        obj = db.get(self.model, id)
        if obj:
            with self.auto_commit(db):
                db.delete(obj)
        return obj

class AsyncCRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @asynccontextmanager
    async def auto_commit(self, db: AsyncSession):
        try:
            yield
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        async with self.auto_commit(db):
            db.add(db_obj)
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        async with self.auto_commit(db):
            db.add(db_obj)
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> ModelType | None:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj:
            async with self.auto_commit(db):
                await db.delete(obj)
        return obj