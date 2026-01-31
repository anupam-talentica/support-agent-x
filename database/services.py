"""Service layer for database operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from database.models import AgentExecution, Metric, Session as DBSession, Task, Ticket, User


class TicketService:
    """Service for ticket operations."""

    @staticmethod
    def create_ticket(
        db: Session,
        user_id: str,
        title: str,
        description: str,
        priority: str = 'P3',
    ) -> Ticket:
        """Create a new ticket."""
        ticket = Ticket(
            ticket_id=str(uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            status='open',
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID."""
        return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    @staticmethod
    def update_ticket_status(
        db: Session, ticket_id: str, status: str, resolved_at: Optional[datetime] = None
    ) -> Optional[Ticket]:
        """Update ticket status."""
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if ticket:
            ticket.status = status
            ticket.updated_at = datetime.utcnow()
            if status == 'resolved' and resolved_at:
                ticket.resolved_at = resolved_at
            db.commit()
            db.refresh(ticket)
        return ticket

    @staticmethod
    def list_tickets(
        db: Session,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets with optional filters."""
        query = db.query(Ticket)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if status:
            query = query.filter(Ticket.status == status)
        return query.order_by(Ticket.created_at.desc()).limit(limit).all()


class TaskService:
    """Service for task operations."""

    @staticmethod
    def create_task(
        db: Session,
        context_id: str,
        ticket_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            task_id=str(uuid4()),
            ticket_id=ticket_id,
            context_id=context_id,
            agent_name=agent_name,
            status='submitted',
            input_data=input_data,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(
        db: Session, task_id: str, status: str, output_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Task]:
        """Update task status."""
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            task.status = status
            if output_data:
                task.output_data = output_data
            if status in ['completed', 'failed']:
                task.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return db.query(Task).filter(Task.task_id == task_id).first()

    @staticmethod
    def get_tasks_by_context(db: Session, context_id: str) -> List[Task]:
        """Get all tasks for a context."""
        return db.query(Task).filter(Task.context_id == context_id).order_by(Task.created_at).all()


class ExecutionService:
    """Service for agent execution logging."""

    @staticmethod
    def log_execution(
        db: Session,
        task_id: str,
        agent_name: str,
        tool_name: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> AgentExecution:
        """Log an agent execution."""
        execution = AgentExecution(
            execution_id=str(uuid4()),
            task_id=task_id,
            agent_name=agent_name,
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            error_message=error_message,
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    @staticmethod
    def get_executions_by_task(db: Session, task_id: str) -> List[AgentExecution]:
        """Get all executions for a task."""
        return (
            db.query(AgentExecution)
            .filter(AgentExecution.task_id == task_id)
            .order_by(AgentExecution.timestamp)
            .all()
        )

    @staticmethod
    def get_executions_by_agent(
        db: Session, agent_name: str, limit: int = 100
    ) -> List[AgentExecution]:
        """Get recent executions for an agent."""
        return (
            db.query(AgentExecution)
            .filter(AgentExecution.agent_name == agent_name)
            .order_by(AgentExecution.timestamp.desc())
            .limit(limit)
            .all()
        )


class MetricService:
    """Service for observability metrics."""

    @staticmethod
    def record_metric(
        db: Session,
        metric_type: str,
        value: Dict[str, Any],
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Metric:
        """Record a metric."""
        metric = Metric(
            metric_id=str(uuid4()),
            agent_name=agent_name,
            metric_type=metric_type,
            value=value,
            metric_metadata=metadata,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def get_metrics(
        db: Session,
        agent_name: Optional[str] = None,
        metric_type: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Metric]:
        """Get metrics with optional filters."""
        query = db.query(Metric)
        if agent_name:
            query = query.filter(Metric.agent_name == agent_name)
        if metric_type:
            query = query.filter(Metric.metric_type == metric_type)
        return query.order_by(Metric.timestamp.desc()).limit(limit).all()


class UserService:
    """Service for user operations."""

    @staticmethod
    def create_user(db: Session, user_id: str, email: str, role: str = 'customer') -> User:
        """Create a new user."""
        user = User(user_id=user_id, email=email, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()


class SessionService:
    """Service for session operations."""

    @staticmethod
    def create_session(
        db: Session, session_id: str, user_id: str, context_id: Optional[str] = None
    ) -> DBSession:
        """Create a new session."""
        session = DBSession(
            session_id=session_id, user_id=user_id, context_id=context_id, is_active=1
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[DBSession]:
        """Get session by ID."""
        return db.query(DBSession).filter(DBSession.session_id == session_id).first()

    @staticmethod
    def update_session_activity(db: Session, session_id: str) -> Optional[DBSession]:
        """Update session last activity timestamp."""
        session = db.query(DBSession).filter(DBSession.session_id == session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
