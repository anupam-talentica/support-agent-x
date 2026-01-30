"""Tests for database models and services."""

import pytest
from sqlalchemy.orm import Session

from database.connection import get_db, init_database
from database.models import AgentExecution, Task, Ticket, User
from database.services import (
    ExecutionService,
    MetricService,
    TaskService,
    TicketService,
    UserService,
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    init_database()
    with get_db() as db:
        yield db


def test_user_service_create(db_session: Session):
    """Test user creation."""
    user = UserService.create_user(
        db_session, user_id='test_001', email='test@example.com', role='customer'
    )
    assert user.user_id == 'test_001'
    assert user.email == 'test@example.com'
    assert user.role == 'customer'


def test_user_service_get(db_session: Session):
    """Test user retrieval."""
    UserService.create_user(db_session, user_id='test_002', email='test2@example.com')
    user = UserService.get_user(db_session, 'test_002')
    assert user is not None
    assert user.email == 'test2@example.com'


def test_ticket_service_create(db_session: Session):
    """Test ticket creation."""
    UserService.create_user(db_session, user_id='user_001', email='user@example.com')
    ticket = TicketService.create_ticket(
        db_session,
        user_id='user_001',
        title='Test Ticket',
        description='Test description',
        priority='P1',
    )
    assert ticket.ticket_id is not None
    assert ticket.title == 'Test Ticket'
    assert ticket.status == 'open'
    assert ticket.priority == 'P1'


def test_ticket_service_update_status(db_session: Session):
    """Test ticket status update."""
    UserService.create_user(db_session, user_id='user_002', email='user2@example.com')
    ticket = TicketService.create_ticket(
        db_session, user_id='user_002', title='Test', description='Test'
    )
    updated = TicketService.update_ticket_status(db_session, ticket.ticket_id, 'resolved')
    assert updated.status == 'resolved'
    assert updated.resolved_at is not None


def test_task_service_create(db_session: Session):
    """Test task creation."""
    task = TaskService.create_task(
        db_session, context_id='ctx_001', agent_name='test_agent', input_data={'test': 'data'}
    )
    assert task.task_id is not None
    assert task.context_id == 'ctx_001'
    assert task.status == 'submitted'


def test_execution_service_log(db_session: Session):
    """Test execution logging."""
    task = TaskService.create_task(db_session, context_id='ctx_002')
    execution = ExecutionService.log_execution(
        db_session,
        task_id=task.task_id,
        agent_name='test_agent',
        tool_name='test_tool',
        input_data={'input': 'test'},
        output_data={'output': 'result'},
        duration_ms=100,
    )
    assert execution.execution_id is not None
    assert execution.agent_name == 'test_agent'
    assert execution.duration_ms == 100


def test_metric_service_record(db_session: Session):
    """Test metric recording."""
    metric = MetricService.record_metric(
        db_session,
        metric_type='latency',
        value={'avg_ms': 150, 'p95_ms': 200},
        agent_name='test_agent',
    )
    assert metric.metric_id is not None
    assert metric.metric_type == 'latency'
    assert metric.agent_name == 'test_agent'


def test_database_relationships(db_session: Session):
    """Test database relationships."""
    user = UserService.create_user(db_session, user_id='rel_user', email='rel@example.com')
    ticket = TicketService.create_ticket(
        db_session, user_id=user.user_id, title='Rel Test', description='Test'
    )
    task = TaskService.create_task(db_session, ticket_id=ticket.ticket_id, context_id='ctx_rel')
    
    # Verify relationships
    assert ticket.user_id == user.user_id
    assert task.ticket_id == ticket.ticket_id
    assert len(user.tickets) == 1
    assert len(ticket.tasks) == 1
