# Database Setup Guide

## Overview

This project uses **three separate databases** as per the architecture:

1. **Application Database (PostgreSQL)** - Core application data
2. **Memory Database (SQLite)** - Memory Agent's three memory types  
3. **Vector Database (ChromaDB)** - Document embeddings for RAG

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Start everything (PostgreSQL + Application)
docker-compose up --build

# Database will be automatically initialized with schema and test data
# UI will be available at http://localhost:12000
```

## Manual Setup

### 1. Start PostgreSQL

**Option A: Docker (Recommended)**
```bash
docker-compose up postgres -d
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb support_agents_db

# Or using psql
psql -U postgres -c "CREATE DATABASE support_agents_db;"
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and set:
DATABASE_URL=postgresql://support_user:support_pass@localhost:5432/support_agents_db
GOOGLE_API_KEY=your_api_key_here
```

### 3. Initialize Databases

```bash
# Application database (PostgreSQL)
python scripts/init_db.py --seed

# Memory database (SQLite)
python agents/memory_agent/scripts/init_memory_db.py
```

### 4. Verify Setup

```python
# Test database connection
python -c "from database.connection import verify_database_connection; assert verify_database_connection(); print('✅ Database connected!')"

# Check tables
python -c "from database.schema import get_table_names; print('Tables:', get_table_names())"
```

## Database Schema

### Application Database (PostgreSQL)

**Users Table**
- `user_id` (PK) - Unique user identifier
- `email` - User email (unique)
- `role` - User role (support_analyst, customer, admin)
- `created_at` - Account creation timestamp

**Tickets Table**
- `ticket_id` (PK) - Unique ticket identifier
- `user_id` (FK) - Reference to Users
- `title` - Ticket title
- `description` - Ticket description
- `status` - open, in_progress, resolved, escalated
- `priority` - P0, P1, P2, P3, P4
- `created_at`, `updated_at`, `resolved_at` - Timestamps

**Sessions Table**
- `session_id` (PK) - Unique session identifier
- `user_id` (FK) - Reference to Users
- `context_id` - Conversation context ID
- `created_at`, `last_activity` - Timestamps
- `is_active` - Active flag

**Tasks Table**
- `task_id` (PK) - Unique task identifier
- `ticket_id` (FK) - Optional reference to Tickets
- `context_id` - Conversation context
- `status` - submitted, working, completed, failed
- `agent_name` - Agent that executed the task
- `input_data`, `output_data` - JSON data
- `created_at`, `completed_at` - Timestamps

**AgentExecutions Table**
- `execution_id` (PK) - Unique execution identifier
- `task_id` (FK) - Reference to Tasks
- `agent_name` - Agent name
- `tool_name` - Tool used
- `input_data`, `output_data` - JSON data
- `duration_ms` - Execution duration
- `timestamp` - Execution timestamp
- `error_message` - Error if any

**Metrics Table**
- `metric_id` (PK) - Unique metric identifier
- `agent_name` - Agent name (optional)
- `metric_type` - latency, success_rate, error_rate, throughput
- `value` - JSON metric value
- `timestamp` - Metric timestamp
- `metadata` - Additional context

### Memory Database (SQLite)

**EpisodicMemory Table**
- `incident_id` (PK) - Unique incident identifier
- `query_text` - Original query
- `resolution` - Resolution text
- `outcome` - resolved, escalated, pending
- `tags` - JSON array of tags
- `user_id` - User identifier
- `timestamp` - Incident timestamp
- `metadata` - Additional context

**WorkingMemory Table**
- `session_id` (PK) - Session identifier
- `context_id` - Context identifier
- `task_data` - JSON task context
- `created_at`, `expires_at`, `last_accessed` - Timestamps

**SemanticMemory Table**
- `doc_id` (PK) - Document identifier
- `content_hash` - Content hash (unique)
- `embedding_id` - Link to ChromaDB embedding
- `category` - Document category
- `last_accessed` - Last access timestamp
- `access_count` - Access counter
- `relevance_score` - Average relevance
- `metadata` - Additional context

## Using Database Services

The service layer provides clean APIs for database operations:

```python
from database.connection import get_db
from database.services import TicketService, TaskService, ExecutionService

# Create a ticket
with get_db() as db:
    ticket = TicketService.create_ticket(
        db,
        user_id='user_001',
        title='Payment failing',
        description='Payment service failing for EU users',
        priority='P1'
    )

# Create a task
with get_db() as db:
    task = TaskService.create_task(
        db,
        context_id='ctx_001',
        ticket_id=ticket.ticket_id,
        agent_name='ingestion_agent',
        input_data={'query': 'Payment failing'}
    )

# Log execution
with get_db() as db:
    execution = ExecutionService.log_execution(
        db,
        task_id=task.task_id,
        agent_name='rag_agent',
        tool_name='search_documents',
        input_data={'query': 'payment'},
        output_data={'results': [...]},
        duration_ms=150
    )
```

## Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Add new column to tickets"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

### Check Migration Status
```bash
alembic current
alembic history
```

## Testing

Run database tests:

```bash
# All database tests
pytest tests/test_database.py -v

# Specific test
pytest tests/test_database.py::test_ticket_service_create -v
```

## Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Test connection
psql -U support_user -d support_agents_db -h localhost

# Check connection string
echo $DATABASE_URL
```

### Migration Issues
```bash
# Reset migrations (WARNING: deletes data)
alembic downgrade base
alembic upgrade head

# Or recreate database
python scripts/init_db.py --drop --seed
```

### Memory Database Issues
```bash
# Check file exists
ls -la data/memory.db

# Recreate
python agents/memory_agent/scripts/init_memory_db.py --drop
```

## Production Considerations

1. **Connection Pooling**: Already configured in `connection.py`
2. **Indexes**: All foreign keys and frequently queried columns are indexed
3. **Transactions**: All operations use transactions via context managers
4. **Error Handling**: Proper rollback on errors
5. **Migrations**: Use Alembic for schema versioning
6. **Backups**: Set up regular PostgreSQL backups
7. **Monitoring**: Use `MetricService` for observability

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://support_user:support_pass@localhost:5432/support_agents_db` |
| `MEMORY_DB_PATH` | Path to Memory Agent SQLite DB | `./data/memory.db` |
| `DB_ECHO` | Log SQL queries (debug) | `False` |

## Next Steps

1. ✅ Database setup complete
2. ⏳ Implement agents (use database services)
3. ⏳ Set up RAG vector database
4. ⏳ Integrate with UI
5. ⏳ Add observability metrics
