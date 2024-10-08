from .base import BaseORM

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class AuthorORM(BaseORM):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # real_estate_agent, homeowner, realtor, official_representative, representative_developer, developer, unknown

    advertisement = relationship('AdvertisementOrm', back_populates='author')