from .base import BaseORM

from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

class ViewsORM(BaseORM):
    __tablename__ = 'views'

    id = Column(Integer, primary_key=True)
    advertisement_id = Column(Integer, ForeignKey('advertisement.id'), nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Integer, nullable=False)

    advertisement = relationship("Advertisement", back_populates="views")