import threading
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from groupfilter import DB_URL


BASE = declarative_base()


class Filters(BASE):
    __tablename__ = "filters"
    filters = Column(TEXT, primary_key=True)
    message = Column(TEXT)
    buttons = Column(JSON)
    media_type = Column(TEXT)
    file_id = Column(TEXT)

    def __init__(self, filters, message, buttons=None, media_type=None, file_id=None):
        self.filters = filters
        self.message = message
        self.buttons = buttons
        self.media_type = media_type
        self.file_id = file_id


def start() -> scoped_session:
    engine = create_engine(DB_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = threading.RLock()


async def add_filter(filters, message, buttons=None, media_type=None, file_id=None):
    with INSERTION_LOCK:
        try:
            fltr = SESSION.query(Filters).filter(Filters.filters.ilike(filters)).one()
        except NoResultFound:
            fltr = Filters(filters=filters, message=message, buttons=buttons, media_type=media_type, file_id=file_id)
            SESSION.add(fltr)
            SESSION.commit()
            return True


async def is_filter(filters):
    with INSERTION_LOCK:
        try:
            fltr = SESSION.query(Filters).filter(Filters.filters.ilike(filters)).one()
            return fltr
        except NoResultFound:
            return False


async def rem_filter(filters):
    with INSERTION_LOCK:
        try:
            fltr = SESSION.query(Filters).filter(Filters.filters.ilike(filters)).one()
            SESSION.delete(fltr)
            SESSION.commit()
            return True
        except NoResultFound:
            return False


async def list_filters():
    try:
        fltrs = SESSION.query(Filters.filters).all()
        return [fltr[0] for fltr in fltrs]
    except NoResultFound:
        return False
    finally:
        SESSION.close()
