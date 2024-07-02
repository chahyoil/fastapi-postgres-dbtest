from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import contextmanager
from fastapi.encoders import jsonable_encoder

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
        obj = db.query(self.model).get(id)
        if obj:
            with self.auto_commit(db):
                db.delete(obj)
        return obj