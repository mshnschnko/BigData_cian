from .base import BaseORM

from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

class PriceORM(BaseORM):
    __tablename__ = 'price'

    advertisement_id = Column(Integer, ForeignKey('advertisement.id'), nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Integer, nullable=False)

    advertisement = relationship("AdvertisementORM", back_populates="price")