# Collaborative Support Agents System

A production-grade multi-agent support system built with A2A protocol, featuring RAG, persistent memory, guardrails, and real-time observability.

## Architecture

The system consists of 8 specialized agents:

1. **Ingestion Agent** - Normalizes incoming tickets and queries
2. **Planner Agent** - Orchestrates execution strategy (serial/parallel/async)
3. **Intent & Classification Agent** - Detects intent, urgency, SLA risk
4. **Knowledge Retrieval Agent (RAG)** - Searches large documents
5. **Memory Agent** - Manages episodic, working, and semantic memory
6. **Reasoning/Correlation Agent** - Connects issues with history
7. **Response Synthesis Agent** - Generates human-readable outputs
8. **Guardrails & Policy Agent** - Applies safety rules and escalation

## Database Architecture

The system uses **three separate databases**:

1. **Application Database (PostgreSQL)**: Tickets, sessions, tasks, metrics

   - Location: PostgreSQL container (docker-compose)
   - Managed by: `database/` module

2. **Memory Database (SQLite)**: Memory Agent's three memory types

   - Location: `data/memory.db`
   - Managed by: `agents/memory_agent/memory_db.py`

3. **Vector Database (ChromaDB)**: Document embeddings for RAG
   - Location: `data/vector_db/`
   - Managed by: `agents/rag_agent/vector_store.py`

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Google API key (for LLM)

### Setup

1. **Clone and navigate to project**:

   ```bash
   cd support_agents
   ```

2. **Create `.env` file**:

   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Start with Docker Compose**:

   ```bash
   docker-compose up --build
   ```

   This will:

   - Start PostgreSQL database
   - Initialize database schema
   - Seed test data
   - Start all agent servers
   - Start UI on http://localhost:12000

4. **Access the application**:
   - UI: http://localhost:12000
   - Host Agent: http://localhost:8083
   - Individual agents: http://localhost:10001-10008

## Observability (Langfuse)

The Host Agent can send traces to [Langfuse](https://langfuse.com/docs) so you can see how each request progresses through the orchestrator (Ingestion → Planner → …). Set `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in `.env` to enable; if unset, the app runs without observability. See [agents/host_agent/OBSERVABILITY.md](agents/host_agent/OBSERVABILITY.md) for setup and usage.

## Local Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16+ (or use Docker for PostgreSQL only)
- uv package manager (recommended) or pip

### Setup

1. **Install dependencies**:

   ```bash
   uv pip install -r pyproject.toml
   # OR
   pip install -e .
   ```

2. **Start PostgreSQL** (if not using Docker):

   ```bash
   docker-compose up postgres -d
   ```

3. **Start ChromaDB Server** (required for RAG agent):

   ```bash
   # Start ChromaDB listening on all interfaces (required for Docker)
   chroma run --host 0.0.0.0 --port 8000
   ```

4. **Initialize databases**:

   ```bash
   # Application database
   python scripts/init_db.py --seed

   # Memory database
   python agents/memory_agent/scripts/init_memory_db.py
   ```

   **Note:** ChromaDB must be started with `--host 0.0.0.0` (not `localhost` or `127.0.0.1`) to allow Docker containers to connect via `host.docker.internal`.

5. **Start agents**:

   ```bash
   # Option 1: Use script
   chmod +x scripts/start_all_agents.sh
   ./scripts/start_all_agents.sh

   # Option 2: Start individually
   python -m agents.host_agent.__main__
   python -m agents.ingestion_agent.__main__
   # ... etc
   ```

6. **Start UI**:
   ```bash
   python -m ui.main
   ```

## Database Management

### Initialize Database

```bash
# Application database
python scripts/init_db.py --seed

# Memory database
python agents/memory_agent/scripts/init_memory_db.py
```

### Database Migrations (Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Database Connection

The application uses PostgreSQL by default. Connection string:

```
postgresql://support_user:support_pass@localhost:5432/support_agents_db
```

Set `DATABASE_URL` in `.env` to customize.

### ChromaDB Setup

ChromaDB is required for the RAG agent. Start it with:

```bash
# Start ChromaDB server (must use 0.0.0.0 for Docker compatibility)
chroma run --host 0.0.0.0 --port 8000
```

**Important:** Use `--host 0.0.0.0` (not `localhost` or `127.0.0.1`) to allow Docker containers to connect.

After starting ChromaDB, ingest documents:

```bash
python scripts/ingest_rag_data.py
```

## Project Structure

```
support_agents/
├── agents/              # All agent implementations
│   ├── host_agent/     # Orchestrator
│   ├── ingestion_agent/
│   ├── planner_agent/
│   ├── intent_agent/
│   ├── rag_agent/      # RAG with document processing
│   ├── memory_agent/   # Memory management
│   ├── reasoning_agent/
│   ├── response_agent/
│   └── guardrails_agent/
├── database/           # Application database module
│   ├── models.py       # SQLAlchemy models
│   ├── connection.py   # DB connection
│   ├── services.py     # Service layer
│   └── migrations/     # Alembic migrations
├── ui/                 # Mesop UI
├── utils/              # Shared utilities
├── tests/              # Test suite
├── data/               # Data storage
│   ├── memory.db       # Memory Agent DB
│   └── vector_db/      # ChromaDB
├── monitoring/         # Observability
├── scripts/            # Utility scripts
├── docker-compose.yml  # Docker setup
├── Dockerfile          # Application container
└── pyproject.toml      # Dependencies
```

## Environment Variables

Key variables (set in `.env`):

- `CHROMA_COLLECTION`: ChromaDB collection name. Use `support-agent-x-openai` (default, for HTTP/OpenAI ingest) or `support-agent-x` (for chromadb-package ingest). Ingest and RAG agent must use the same value.
- `CHROMA_HOST`, `CHROMA_PORT`: ChromaDB server (default localhost:8000)
- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_API_KEY`: Google AI API key
- `MEMORY_DB_PATH`: Path to Memory Agent SQLite DB

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_database.py
pytest tests/test_rag.py
pytest tests/test_memory.py
```

## Development Workflow

1. **Database changes**: Create Alembic migration
2. **Agent changes**: Update agent code, restart agent server
3. **UI changes**: Changes hot-reload automatically (Mesop)
4. **Dependencies**: Update `pyproject.toml`, run `uv pip install`

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`
- Verify database exists: `psql -U support_user -d support_agents_db`

### Agent Not Starting

- Check port availability: `lsof -i :PORT`
- Verify environment variables are loaded
- Check agent logs for errors

### Memory Not Persisting

- Verify `data/memory.db` file exists and is writable
- Check Memory Agent database initialization

## License

[Your License Here]

## Contributors

[Your Team]
