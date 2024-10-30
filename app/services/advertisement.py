from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging

from db.models import AdvertisementORM
from .base import BaseService

class AdvertisementService(BaseService):
    model = AdvertisementORM
