"""Database connection and initialization for Memory Agent's SQLite database."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from agents.memory_agent.memory_schema import Base

# Memory database path (separate from application DB)
MEMORY_DB_PATH = os.getenv('MEMORY_DB_PATH', './data/memory.db')

# Ensure directory exists
os.makedirs(os.path.dirname(MEMORY_DB_PATH), exist_ok=True)

# Create SQLite engine
MEMORY_DB_URL = f'sqlite:///{MEMORY_DB_PATH}'
engine = create_engine(
    MEMORY_DB_URL,
    connect_args={'check_same_thread': False},  # SQLite specific
    echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for foreign keys."""
    cursor = dbapi_conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


def init_memory_database() -> None:
    """Initialize memory database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print(f'Memory database initialized at {MEMORY_DB_PATH}')


def drop_memory_database() -> None:
    """Drop all memory tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print('Memory database dropped successfully')


@contextmanager
def get_memory_db() -> Generator[Session, None, None]:
    """Get memory database session context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_memory_db_session() -> Session:
    """Get a memory database session."""
    return SessionLocal()
