# Memory Agent Integration Guide

## Overview

The Memory Agent provides intelligent conversational memory for the support ticket system using **mem0** (Memory Zero). It enables the system to remember user preferences, past issues, and resolutions across sessions by leveraging ChromaDB and OpenAI.

## 🚀 Quick Start

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Install core dependencies
# Note: chromadb is usually installed via the [rag] extra
pip install mem0ai openai chromadb python-dotenv

# 3. Set environment variable
export OPENAI_API_KEY=sk-your-key-here

# 4. Ensure ChromaDB is running
# If chromadb is not installed, install it first.
chroma run --host 0.0.0.0 --port 8000

# 5. Start Memory Agent
python -m agents.memory_agent.__main__
```

The Memory Agent will be available at: `http://localhost:10005`

---

## 🏗️ Architecture

### Technology Stack
- **mem0** - Intelligent memory layer with LLM-powered fact extraction
- **ChromaDB** - Vector store (shared with RAG system)
- **OpenAI** - LLM for fact extraction and embeddings (gpt-4o-mini)
- **SQLite** - Used by mem0 for history tracking (`./data/mem0_history.db`)

### Components
1. **Mem0MemoryAgent** (`memory_agent.py`)
   - Core memory operations (add, search, update, delete)
   - Ticket-specific memory management
   - Similar ticket recall

2. **MemoryTools** (`memory_tools.py`)
   - Tool wrappers for ADK integration
   - Async methods for agent communication
   - **Robust Response Handling**: Automatically handles various `mem0` return formats (dict or list) and ensures stable integration.

3. **Mem0Config** (`mem0_config.py`)
   - Configuration for ChromaDB integration
   - LLM and embedding settings

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required for mem0
OPENAI_API_KEY=sk-your-key-here

# ChromaDB (shared with RAG)
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Optional mem0 settings
OPENAI_MODEL=gpt-4o-mini  # Model for fact extraction
MEM0_HISTORY_DB_PATH=./data/mem0_history.db
```

### ChromaDB Setup
mem0 uses your existing ChromaDB instance on port 8000. It creates a separate collection `mem0_memories` to avoid conflicts with other RAG collections.

## 🔄 Integration Flow

1. **Ticket Ingestion**: Planner Agent receives a ticket.
2. **Memory Search**: 
   - Planner queries Memory Agent: `await tools.find_similar_tickets(query=description, user_id=user_id)`
   - *Happens in parallel with Intent Classification*
3. **Response Generation**: 
   - Response Agent receives: Classification + Memory Context + RAG Knowledge
   - "I see you had a similar issue last week (TKT-123) which was resolved by..."
4. **Resolution Storage**: 
   - After responding, Planner stores the resolution: `await tools.store_ticket_resolution(...)`

## 🛠️ Memory Tools API

All methods are `async` and return a structured dictionary.

### 1. `store_context`
Store important information about user interactions.
```python
result = await tools.store_context(
    information="User prefers email notifications",
    user_id="user123",
    ticket_id="TKT-001"  # optional
)
# Returns: {"status": "success", "message": "...", "memory_ids": [...]}
```

### 2. `recall_context`
Search for relevant past interactions.
```python
result = await tools.recall_context(
    query="notification preferences",
    user_id="user123",
    limit=5
)
# Returns: {"status": "success", "count": 1, "memories": [{"content": "...", "relevance": 0.95, ...}]}
```

### 3. `get_user_history`
Get complete interaction history for a user.
```python
result = await tools.get_user_history(user_id="user123")
# Returns: {"status": "success", "user_id": "...", "total_memories": 5, "memories": [...]}
```

### 4. `store_ticket_resolution`
Store a complete ticket with its resolution.
```python
result = await tools.store_ticket_resolution(
    ticket_id="TKT-001",
    user_id="user123",
    query="Payment failing",
    classification={"incident_type": "payment", "urgency": "P2"},
    resolution="Updated card on file"
)
```

### 5. `find_similar_tickets`
Find similar past tickets (scoped to user or global).
```python
result = await tools.find_similar_tickets(
    query="Dashboard not loading",
    user_id="user123",  # Use "all_users" for global search
    limit=3
)
# Returns: {"status": "success", "count": 2, "similar_tickets": [...]}
```

## 🧪 Testing

### Run Integration Test
Always run tests from the virtual environment:
```bash
source venv/bin/activate
python3 tests/test_memory_integration.py
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'mem0'` | `pip install mem0ai` in the active venv. |
| `OPENAI_API_KEY not set` | Add to `.env` and ensure `load_dotenv()` is called. |
| `Failed to connect to ChromaDB` | Ensure `chroma run` is active on port 8000. |
| `pydantic` errors | Ensure `pydantic` and `pydantic-core` are correctly installed in the venv. |
| `AttributeError: 'str' object has no attribute 'get'` | This occurs if `mem0` returns raw strings. **Fixed** in the current `memory_tools.py` implementation which now handles both `dict` and `str` return types. |

## ✅ Best Practices

1. **Store Resolutions**: Don't just store the problem; store the *successful resolution*. This allows future agents to reuse the solution.
2. **Global Search**: Use `user_id="all_users"` in `find_similar_tickets` to detect system-wide patterns (e.g., a sudden spike in login issues).
3. **Persistence**: Memories are stored in ChromaDB and metadata in `./data/mem0_history.db`. Ensure these paths are backed up.
