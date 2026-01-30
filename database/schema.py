"""Database schema definitions and utilities."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from database.connection import engine
from database.models import Base


def get_table_names() -> list[str]:
    """Get list of all table names in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get schema information for a specific table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return {
        'table_name': table_name,
        'columns': [
            {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': str(col.get('default', '')),
            }
            for col in columns
        ],
    }


def verify_database_connection() -> bool:
    """Verify database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False


def get_database_stats(db: Session) -> Dict[str, Any]:
    """Get database statistics."""
    from database.models import Ticket, Task, AgentExecution, User

    stats = {
        'users': db.query(User).count(),
        'tickets': db.query(Ticket).count(),
        'tasks': db.query(Task).count(),
        'executions': db.query(AgentExecution).count(),
        'tickets_by_status': {},
        'tickets_by_priority': {},
    }

    # Count tickets by status
    for status in ['open', 'in_progress', 'resolved', 'escalated']:
        stats['tickets_by_status'][status] = (
            db.query(Ticket).filter(Ticket.status == status).count()
        )

    # Count tickets by priority
    for priority in ['P0', 'P1', 'P2', 'P3', 'P4']:
        stats['tickets_by_priority'][priority] = (
            db.query(Ticket).filter(Ticket.priority == priority).count()
        )

    return stats
