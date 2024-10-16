from .base import BaseORM

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class AdvertisementORM(BaseORM):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    adv_type = Column(String, nullable=False) # rent_long, sale
    object_id = Column(Integer, ForeignKey('object.id'), nullable=False)
    url = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    amount_of_views = Column(Integer)
    publication_date = Column(Date)
    unpublish_date = Column(Date)

    author = relationship('AuthorORM', back_populates="advertisement")
    object = relationship('ObjectORM', back_populates="advertisement")
    price = relationship('PriceORM', back_populates="advertisement")
    views = relationship('ViewsORM', back_populates="advertisement")