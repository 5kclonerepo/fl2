import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import QueuePool
from groupfilter import DB_URL, LOGGER
import inspect


BASE = declarative_base()


class Promos(BASE):
    __tablename__ = "promos"
    link = Column(TEXT, primary_key=True)
    text = Column(TEXT)

    def __init__(self, link, text):
        self.link = link
        self.text = text


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


async def add_promo(link, text):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                promo = session.query(Promos).filter(Promos.link.ilike(link)).one()
                return False
        except NoResultFound:
            try:
                with session_scope() as session:
                    promo = Promos(link=link, text=text)
                    session.add(promo)
                    return True
            except Exception as e:
                LOGGER.error("Error adding promo: %s", str(e))
                return False


async def del_promo(link):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                promo = session.query(Promos).filter(Promos.link.ilike(link)).one()
                session.delete(promo)
                return True
        except NoResultFound:
            return False
        except Exception as e:
            LOGGER.error("Error deleting promo: %s", str(e))
            return False


async def get_promos():
    try:
        with session_scope() as session:
            promos = session.query(Promos).all()
            return [{
                "link": promo.link,
                "text": promo.text
            } for promo in promos]
    except Exception as e:
        LOGGER.error("Error getting promos: %s", str(e))
        return None
