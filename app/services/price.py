from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging

from db.models import PriceORM
from .base import BaseService

class PriceService(BaseService):
    model = PriceORM
