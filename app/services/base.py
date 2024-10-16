from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from typing import Optional
import logging

from db.models import BaseORM

class BaseService:
    model = BaseORM

    @classmethod
    def get_by_id(cls, db: Session, id: int) -> Optional[model]:
        obj = db.query(cls.model).filter(cls.model.id == id).first()
        return obj
    
    @classmethod
    def get_all(cls, db: Session) -> list:
        return db.query(cls.model).all()
    
    @classmethod
    def del_by_id(cls, db: Session, id: int) -> bool:
        obj = cls.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        else:
            return False
        
    @classmethod
    def create(cls, db: Session, data: dict) -> bool:
        obj = cls.model(**data)
        try:
            db.add(obj)
            db.commit()
            return True
        except SQLAlchemyError as e:
            logging.error(e)
            db.rollback()
            return False