from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging

from db.models import ViewsORM
from .base import BaseService

class ViewsService(BaseService):
    model = ViewsORM
