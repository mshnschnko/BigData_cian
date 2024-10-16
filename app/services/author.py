from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import logging

from db.models import AuthorORM
from .base import BaseService

class AuthorService(BaseService):
    model = AuthorORM
