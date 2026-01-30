"""Database connection management for PostgreSQL."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base


# Database configuration from environment variables
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://support_user:support_pass@localhost:5432/support_agents_db',
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv('DB_ECHO', 'False').lower() == 'true',  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas if using SQLite (for fallback)."""
    if 'sqlite' in DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


def init_database() -> None:
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    print(f'Database initialized successfully at {DATABASE_URL}')


def drop_database() -> None:
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print('Database dropped successfully')


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session (for dependency injection)."""
    return SessionLocal()
