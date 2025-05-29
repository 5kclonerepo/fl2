import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import QueuePool
from groupfilter import DB_URL, LOGGER
import inspect


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
    engine = create_engine(
        DB_URL,
        client_encoding="utf8",
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=50,
        pool_timeout=10,
        pool_recycle=1800,
        pool_pre_ping=True,
        pool_use_lifo=True,
    )
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = threading.RLock()


@contextmanager
def session_scope():
    try:
        yield SESSION
        SESSION.commit()
    except Exception as e:
        SESSION.rollback()
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name if caller_frame else "unknown"
        LOGGER.error("Database error occurred in function '%s': %s", caller_name, str(e))
        raise
    finally:
        SESSION.close()


async def add_filter(filters, message=None, buttons=None, media_type=None, file_id=None):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                fltr = session.query(Filters).filter(Filters.filters.ilike(filters)).one_or_none()
                if fltr:
                    return False
        except Exception as e:
            LOGGER.error("Database error while checking filter: %s", str(e))
            return False

        try:
            with session_scope() as session:
                fltr = Filters(
                    filters=filters,
                    message=message,
                    buttons=buttons,
                    media_type=media_type,
                    file_id=file_id,
                )
                session.add(fltr)
                return True
        except Exception as e:
            LOGGER.error("Error adding filter: %s", str(e))
            return False


async def is_filter(filters):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                fltr = (
                    session.query(Filters).filter(Filters.filters.ilike(filters)).one_or_none()
                )
                if fltr:
                    return {
                        "filters": fltr.filters,
                            "file_id": fltr.file_id,
                            "message": fltr.message,
                            "buttons": fltr.buttons,
                            "media_type": fltr.media_type
                        }
                else:
                    return False
        except NoResultFound:
            return False
        except Exception as e:
            LOGGER.error("Error checking filter: %s", str(e))
            return False


async def rem_filter(filters):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                fltr = (
                    session.query(Filters).filter(Filters.filters.ilike(filters)).one()
                )
                session.delete(fltr)
                return True
        except NoResultFound:
            return False
        except Exception as e:
            LOGGER.error("Error removing filter: %s", str(e))
            return False


async def list_filters():
    try:
        with session_scope() as session:
            fltrs = session.query(Filters.filters).all()
            return [fltr[0] for fltr in fltrs]
    except Exception as e:
        LOGGER.error("Error listing filters: %s", str(e))
        return False
