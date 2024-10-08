from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker
from config import DB_URI

_engine = create_engine(DB_URI)
_session_factory = sessionmaker(autoflush=True, bind=_engine)

def disconnect_db():
    _session_factory.close_all()
    _engine.dispose()

def create_session() -> Session:
    return _session_factory()

def get_session_factory() -> sessionmaker:
    return _session_factory

def get_db():
    db = create_session()
    try:
        yield db
    finally:
        db.close()