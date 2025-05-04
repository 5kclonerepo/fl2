import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import Column, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from groupfilter import DB_URL, LOGGER
import inspect


BASE = declarative_base()


class BanList(BASE):
    __tablename__ = "banlist"
    user_id = Column(BigInteger, primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id


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


async def ban_user(user_id):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                usr = session.query(BanList).filter_by(user_id=user_id).one_or_none()
                if not usr:
                    usr = BanList(user_id=user_id)
                    session.add(usr)
                    return True
                return False
        except Exception as e:
            LOGGER.error("Error banning user: %s", str(e))
            return False


async def is_banned(user_id):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                usr = session.query(BanList).filter_by(user_id=user_id).one_or_none()
                return usr.user_id if usr else False
        except Exception as e:
            LOGGER.error("Error checking ban status: %s", str(e))
            return False


async def unban_user(user_id):
    with INSERTION_LOCK:
        try:
            with session_scope() as session:
                usr = session.query(BanList).filter_by(user_id=user_id).one_or_none()
                if usr:
                    session.delete(usr)
                    return True
                return False
        except Exception as e:
            LOGGER.error("Error unbanning user: %s", str(e))
            return False
