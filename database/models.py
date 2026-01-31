"""SQLAlchemy models for the application database."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for support analysts, customers, and admins."""

    __tablename__ = 'users'

    user_id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=False)  # 'support_analyst', 'customer', 'admin'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    tickets = relationship('Ticket', back_populates='user')
    sessions = relationship('Session', back_populates='user')

    def __repr__(self) -> str:
        return f'<User(user_id={self.user_id}, email={self.email}, role={self.role})>'


class Ticket(Base):
    """Support ticket model."""

    __tablename__ = 'tickets'

    ticket_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        String(50), nullable=False, default='open'
    )  # 'open', 'in_progress', 'resolved', 'escalated'
    priority = Column(
        String(10), nullable=False, default='P3'
    )  # 'P0', 'P1', 'P2', 'P3', 'P4'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship('User', back_populates='tickets')
    tasks = relationship('Task', back_populates='ticket')

    # Indexes for performance
    __table_args__ = (
        Index('idx_ticket_user_id', 'user_id'),
        Index('idx_ticket_status', 'status'),
        Index('idx_ticket_priority', 'priority'),
        Index('idx_ticket_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f'<Ticket(ticket_id={self.ticket_id}, title={self.title}, status={self.status})>'


class Session(Base):
    """User session model for tracking conversations."""

    __tablename__ = 'sessions'

    session_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    context_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive

    # Relationships
    user = relationship('User', back_populates='sessions')

    # Indexes
    __table_args__ = (
        Index('idx_session_user_id', 'user_id'),
        Index('idx_session_context_id', 'context_id'),
        Index('idx_session_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f'<Session(session_id={self.session_id}, user_id={self.user_id}, context_id={self.context_id})>'


class Task(Base):
    """Task model for tracking agent task execution."""

    __tablename__ = 'tasks'

    task_id = Column(String(255), primary_key=True)
    ticket_id = Column(String(255), ForeignKey('tickets.ticket_id'), nullable=True)
    context_id = Column(String(255), nullable=False)
    status = Column(
        String(50), nullable=False, default='submitted'
    )  # 'submitted', 'working', 'completed', 'failed'
    agent_name = Column(String(100), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    ticket = relationship('Ticket', back_populates='tasks')
    executions = relationship('AgentExecution', back_populates='task')

    # Indexes
    __table_args__ = (
        Index('idx_task_ticket_id', 'ticket_id'),
        Index('idx_task_context_id', 'context_id'),
        Index('idx_task_status', 'status'),
        Index('idx_task_agent_name', 'agent_name'),
        Index('idx_task_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f'<Task(task_id={self.task_id}, ticket_id={self.ticket_id}, status={self.status})>'


class AgentExecution(Base):
    """Agent execution log for observability."""

    __tablename__ = 'agent_executions'

    execution_id = Column(String(255), primary_key=True)
    task_id = Column(String(255), ForeignKey('tasks.task_id'), nullable=False)
    agent_name = Column(String(100), nullable=False)
    tool_name = Column(String(200), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    task = relationship('Task', back_populates='executions')

    # Indexes
    __table_args__ = (
        Index('idx_execution_task_id', 'task_id'),
        Index('idx_execution_agent_name', 'agent_name'),
        Index('idx_execution_timestamp', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f'<AgentExecution(execution_id={self.execution_id}, agent_name={self.agent_name}, tool_name={self.tool_name})>'


class Metric(Base):
    """Observability metrics model."""

    __tablename__ = 'metrics'

    metric_id = Column(String(255), primary_key=True)
    agent_name = Column(String(100), nullable=True)
    metric_type = Column(String(100), nullable=False)  # 'latency', 'success_rate', 'error_rate', 'throughput'
    value = Column(JSON, nullable=False)  # Can store numeric or complex metrics
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_metadata = Column('metadata', JSON, nullable=True)  # Additional context

    # Indexes
    __table_args__ = (
        Index('idx_metric_agent_name', 'agent_name'),
        Index('idx_metric_type', 'metric_type'),
        Index('idx_metric_timestamp', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f'<Metric(metric_id={self.metric_id}, agent_name={self.agent_name}, metric_type={self.metric_type})>'
