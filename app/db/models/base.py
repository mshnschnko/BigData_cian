from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer

class BaseORM(DeclarativeBase):
    __abstract__ = True
    id = Column(Integer, primary_key=True)