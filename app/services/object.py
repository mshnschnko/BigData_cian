from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging

from db.models import ObjectORM
from .base import BaseService

class ObjectService(BaseService):
    model = ObjectORM
