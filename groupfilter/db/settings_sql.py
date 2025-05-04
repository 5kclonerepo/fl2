import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, Boolean, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from groupfilter import DB_URL, LOGGER
import inspect


BASE = declarative_base()


class AdminSettings(BASE):
    __tablename__ = "admin_settings"
    setting_name = Column(TEXT, primary_key=True)
    auto_delete = Column(Numeric)
    custom_caption = Column(TEXT)
    caption_uname = Column(TEXT)
    fsub_channel = Column(Numeric)
    repair_mode = Column(Boolean)
    info_msg = Column(TEXT)
    del_msg = Column(TEXT)
    info_img = Column(TEXT)
    del_img = Column(TEXT)
    notfound_msg = Column(TEXT)
    notfound_img = Column(TEXT)
    fsub_msg = Column(TEXT)
    fsub_img = Column(TEXT)
    btn_del = Column(Numeric)

    def __init__(self, setting_name="default"):
        self.setting_name = setting_name
        self.auto_delete = 0
        self.custom_caption = None
        self.caption_uname = None
        self.fsub_channel = None
        self.repair_mode = False
        self.info_msg = None
        self.del_msg = None
        self.info_img = None
        self.del_img = None
        self.notfound_msg = None
        self.notfound_img = None
        self.fsub_msg = None
        self.fsub_img = None
        self.btn_del = 0


class Settings(BASE):
    __tablename__ = "settings"
    group_id = Column(BigInteger, primary_key=True)
    precise_mode = Column(Boolean)
    button_mode = Column(Boolean)
    link_mode = Column(Boolean)
    list_mode = Column(Boolean)

    def __init__(self, group_id, precise_mode, button_mode, link_mode, list_mode):
        self.group_id = group_id
        self.precise_mode = precise_mode
        self.button_mode = button_mode
        self.link_mode = link_mode
        self.list_mode = list_mode


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


async def get_search_settings(group_id):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                settings = session.query(Settings).filter_by(group_id=group_id).first()
                if settings:
                    return {
                        "group_id": settings.group_id,
                        "precise_mode": settings.precise_mode,
                        "button_mode": settings.button_mode,
                        "link_mode": settings.link_mode,
                        "list_mode": settings.list_mode
                    }
                return None
    except Exception as e:
        LOGGER.error("Error getting search settings: %s", str(e))
        return None


async def change_search_settings(
    group_id, precise_mode=None, button_mode=True, link_mode=None, list_mode=None
):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                settings = session.query(Settings).filter_by(group_id=group_id).first()
                if settings:
                    if precise_mode is not None:
                        settings.precise_mode = precise_mode
                    if button_mode is not None:
                        settings.button_mode = button_mode
                    if link_mode is not None:
                        settings.link_mode = link_mode
                    if list_mode is not None:
                        settings.list_mode = list_mode
                else:
                    new_settings = Settings(
                        group_id=group_id,
                        precise_mode=precise_mode,
                        button_mode=button_mode,
                        link_mode=link_mode,
                        list_mode=list_mode,
                    )
                    session.add(new_settings)
            return True
    except Exception as e:
        LOGGER.warning("Error changing search settings: %s ", str(e))


async def set_repair_mode(repair_mode):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.repair_mode = repair_mode
    except Exception as e:
        LOGGER.error("Error setting repair mode: %s", str(e))


async def set_auto_delete(dur):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.auto_delete = dur
    except Exception as e:
        LOGGER.warning("Error setting auto delete: %s ", str(e))


async def get_admin_settings():
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                return {
                    "setting_name": admin_setting.setting_name,
                    "auto_delete": admin_setting.auto_delete,
                    "custom_caption": admin_setting.custom_caption,
                    "caption_uname": admin_setting.caption_uname,
                    "fsub_channel": admin_setting.fsub_channel,
                    "repair_mode": admin_setting.repair_mode,
                    "info_msg": admin_setting.info_msg,
                    "del_msg": admin_setting.del_msg,
                    "info_img": admin_setting.info_img,
                    "del_img": admin_setting.del_img,
                    "notfound_msg": admin_setting.notfound_msg,
                    "notfound_img": admin_setting.notfound_img,
                    "fsub_msg": admin_setting.fsub_msg,
                    "fsub_img": admin_setting.fsub_img,
                    "btn_del": admin_setting.btn_del
                }
    except Exception as e:
        LOGGER.error("Error getting admin settings: %s", str(e))
        return None


async def set_custom_caption(caption):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.custom_caption = caption
    except Exception as e:
        LOGGER.warning("Error setting custom caption: %s ", str(e))


async def set_captionplus(username):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.caption_uname = username
    except Exception as e:
        LOGGER.warning("Error adding username: %s ", str(e))


async def set_info_msg(message):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.info_msg = message
    except Exception as e:
        LOGGER.warning("Error setting info message: %s ", str(e))


async def set_del_msg(message):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.del_msg = message
            return True
    except Exception as e:
        LOGGER.warning("Error setting delete message: %s ", str(e))
        return False


async def set_info_img(img_id):
    with INSERTION_LOCK:
        with session_scope() as session:
            try:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.info_img = img_id
                return True
            except Exception as e:
                LOGGER.warning("Error setting info image: %s", str(e))
                return False


async def set_del_img(img_id):
    with INSERTION_LOCK:
        with session_scope() as session:
            try:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.del_img = img_id
                return True
            except Exception as e:
                LOGGER.warning("Error setting delete image: %s", str(e))
                return False


async def set_unavail_msg(message):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.notfound_msg = message
                return True
    except Exception as e:
        LOGGER.warning("Error setting delete message: %s ", str(e))
        return False


async def set_unavail_img(img_id):
    with INSERTION_LOCK:
        with session_scope() as session:
            try:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.notfound_img = img_id
                return True
            except Exception as e:
                LOGGER.warning("Error setting not found image: %s", str(e))
                return False


async def set_button_delete(dur):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.btn_del = dur
    except Exception as e:
        LOGGER.warning("Error setting button delete: %s ", str(e))


async def set_fsub_count(count):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.fsub_channel = count
    except Exception as e:
        LOGGER.warning("Error setting fsub count: %s ", str(e))


async def set_fsub_msg(message):
    try:
        with INSERTION_LOCK:
            with session_scope() as session:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.fsub_msg = message
                return True
    except Exception as e:
        LOGGER.warning("Error setting fsub message: %s ", str(e))
        return False


async def set_fsub_img(img_id):
    with INSERTION_LOCK:
        with session_scope() as session:
            try:
                admin_setting = session.query(AdminSettings).first()
                if not admin_setting:
                    admin_setting = AdminSettings(setting_name="default")
                    session.add(admin_setting)

                admin_setting.fsub_img = img_id
                return True
            except Exception as e:
                LOGGER.warning("Error setting fsub image: %s", str(e))
                return False
