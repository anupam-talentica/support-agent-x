"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('idx_user_email', 'users', ['email'], unique=False)

    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('ticket_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('ticket_id'),
    )
    op.create_index('idx_ticket_user_id', 'tickets', ['user_id'], unique=False)
    op.create_index('idx_ticket_status', 'tickets', ['status'], unique=False)
    op.create_index('idx_ticket_priority', 'tickets', ['priority'], unique=False)
    op.create_index('idx_ticket_created_at', 'tickets', ['created_at'], unique=False)

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('context_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('session_id'),
    )
    op.create_index('idx_session_user_id', 'sessions', ['user_id'], unique=False)
    op.create_index('idx_session_context_id', 'sessions', ['context_id'], unique=False)
    op.create_index('idx_session_active', 'sessions', ['is_active'], unique=False)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('ticket_id', sa.String(length=255), nullable=True),
        sa.Column('context_id', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=True),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.ticket_id'], ),
        sa.PrimaryKeyConstraint('task_id'),
    )
    op.create_index('idx_task_ticket_id', 'tasks', ['ticket_id'], unique=False)
    op.create_index('idx_task_context_id', 'tasks', ['context_id'], unique=False)
    op.create_index('idx_task_status', 'tasks', ['status'], unique=False)
    op.create_index('idx_task_agent_name', 'tasks', ['agent_name'], unique=False)
    op.create_index('idx_task_created_at', 'tasks', ['created_at'], unique=False)

    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('execution_id', sa.String(length=255), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('tool_name', sa.String(length=200), nullable=True),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
        sa.PrimaryKeyConstraint('execution_id'),
    )
    op.create_index('idx_execution_task_id', 'agent_executions', ['task_id'], unique=False)
    op.create_index('idx_execution_agent_name', 'agent_executions', ['agent_name'], unique=False)
    op.create_index('idx_execution_timestamp', 'agent_executions', ['timestamp'], unique=False)

    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('metric_id', sa.String(length=255), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=True),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('metric_id'),
    )
    op.create_index('idx_metric_agent_name', 'metrics', ['agent_name'], unique=False)
    op.create_index('idx_metric_type', 'metrics', ['metric_type'], unique=False)
    op.create_index('idx_metric_timestamp', 'metrics', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_metric_timestamp', table_name='metrics')
    op.drop_index('idx_metric_type', table_name='metrics')
    op.drop_index('idx_metric_agent_name', table_name='metrics')
    op.drop_table('metrics')
    op.drop_index('idx_execution_timestamp', table_name='agent_executions')
    op.drop_index('idx_execution_agent_name', table_name='agent_executions')
    op.drop_index('idx_execution_task_id', table_name='agent_executions')
    op.drop_table('agent_executions')
    op.drop_index('idx_task_created_at', table_name='tasks')
    op.drop_index('idx_task_agent_name', table_name='tasks')
    op.drop_index('idx_task_status', table_name='tasks')
    op.drop_index('idx_task_context_id', table_name='tasks')
    op.drop_index('idx_task_ticket_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('idx_session_active', table_name='sessions')
    op.drop_index('idx_session_context_id', table_name='sessions')
    op.drop_index('idx_session_user_id', table_name='sessions')
    op.drop_table('sessions')
    op.drop_index('idx_ticket_created_at', table_name='tickets')
    op.drop_index('idx_ticket_priority', table_name='tickets')
    op.drop_index('idx_ticket_status', table_name='tickets')
    op.drop_index('idx_ticket_user_id', table_name='tickets')
    op.drop_table('tickets')
    op.drop_index('idx_user_email', table_name='users')
    op.drop_table('users')
