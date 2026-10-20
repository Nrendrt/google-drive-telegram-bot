import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from bot import DATABASE_URL, LOGGER

LOCAL_SQLITE_URL = "sqlite:///data/gdrivebot.db"


def _normalize(url):
  if not url:
    return url
  if url.startswith("postgres://"):
    return "postgresql://" + url[len("postgres://"):]
  return url


def _engine_for(url):
  kwargs = {}
  if url.startswith("postgresql"):
    kwargs["connect_args"] = {"connect_timeout": 8}
  elif url.startswith("sqlite"):
    kwargs["connect_args"] = {"check_same_thread": False}
  return create_engine(url, **kwargs)


def _can_connect(url):
  engine = None
  try:
    engine = _engine_for(url)
    with engine.connect() as conn:
      conn.execute(text("SELECT 1"))
    return True
  except (SQLAlchemyError, OSError) as exc:
    LOGGER.warning("Database unavailable (%s).", type(exc).__name__)
    return False
  finally:
    if engine is not None:
      engine.dispose()


def start() -> scoped_session:
  url = _normalize(DATABASE_URL)
  if not url:
    LOGGER.error('Invalid DATABASE_URL : Exiting now.')
    exit(1)
  if not _can_connect(url):
    os.makedirs("data", exist_ok=True)
    LOGGER.warning(
      "Configured database is unreachable. Using local SQLite at data/gdrivebot.db"
    )
    url = LOCAL_SQLITE_URL
  try:
    engine = _engine_for(url)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))
  except ValueError:
    LOGGER.error('Invalid DATABASE_URL : Exiting now.')
    exit(1)


BASE = declarative_base()
SESSION = start()