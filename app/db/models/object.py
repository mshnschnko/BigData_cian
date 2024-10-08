from .base import BaseORM

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

class ObjectORM(BaseORM):
    __tablename__ = 'object'

    id = Column(Integer, primary_key=True)
    district = Column(String, nullable=False)
    underground = Column(String, nullable=False)
    street = Column(String, nullable=False)
    house_num = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    total_floor = Column(Integer, nullable=False)
    total_meters = Column(Float, nullable=False)
    living_meters = Column(Float, nullable=False)
    kitchen_meters = Column(Float, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    year_of_construction = Column(Integer, nullable=False)
    house_material_type = Column(String, nullable=False) 
    commission = Column(Integer, nullable=False)

    advertisement = relationship('AdvertisementOrm', back_populates='object')
    
    
    
'''
1 - киричный
2 - монолитный
3 - панельный
4 - блочный
5 - деревянный
6 - сталинский
7 - щитовой
8 - кирпично-монолитный
'''