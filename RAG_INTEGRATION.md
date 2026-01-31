# RAG Agent Integration with Planner Agent

## Overview

The RAG Agent has been integrated with the Planner Agent. The Planner Agent can now route queries to the RAG Agent to retrieve relevant knowledge from ChromaDB before generating responses.

## Architecture Flow

```
User Ticket
    ↓
Host Agent
    ↓
Ingestion Agent (normalizes ticket)
    ↓
Planner Agent
    ├──→ Intent Classification Agent (classifies ticket)
    ├──→ RAG Agent (retrieves relevant knowledge) ⭐ NEW
    └──→ Response Agent (generates final response with classification + knowledge)
```

## Changes Made

### 1. Planner Agent (`agents/planner_agent/planner_agent.py`)

- ✅ Added RAG Agent to remote agent connections
- ✅ Updated routing instructions to include RAG Agent
- ✅ Updated execution flow: Intent → RAG → Response

### 2. Planner Agent Server (`agents/planner_agent/__main__.py`)

- ✅ Added `RAG_AGENT_URL` to remote agent addresses
- ✅ Default: `http://localhost:10012`

### 3. RAG Agent (`agents/rag_agent/agent.py`)

- ✅ Updated to use environment variables for ChromaDB connection
- ✅ Configurable via `CHROMA_HOST`, `CHROMA_PORT`, `CHROMA_COLLECTION`

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# RAG Agent URL (for Planner Agent to connect)
RAG_AGENT_URL=http://localhost:10012

# ChromaDB Server Connection (for RAG Agent)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=support-agent-x
```

### Agent Ports

| Agent | Port | Description |
|-------|------|-------------|
| RAG Agent | 10012 | Knowledge retrieval from ChromaDB |
| Planner Agent | 10002 | Routes to Intent, RAG, and Response |

## Running the System

### 1. Start ChromaDB Server

Make sure your ChromaDB server is running on `localhost:8000` (or configure via environment variables).

### 2. Start All Agents

```bash
# Terminal 1: Ingestion Agent
python -m agents.ingestion_agent.__main__

# Terminal 2: Intent Agent
python -m agents.intent_agent.__main__

# Terminal 3: RAG Agent
python -m agents.rag_agent.__main__

# Terminal 4: Response Agent
python -m agents.response_agent.__main__

# Terminal 5: Planner Agent (connects to Intent, RAG, Response)
python -m agents.planner_agent.__main__

# Terminal 6: Host Agent (connects to Ingestion, Planner)
python -m agents.host_agent.__main__

# Terminal 7: UI
gunicorn --bind 0.0.0.0:12000 ui.main:me
```

### 3. Verify Integration

1. Submit a ticket via UI
2. Check Planner Agent logs - it should:
   - Connect to RAG Agent
   - Route query to RAG Agent
   - Receive retrieved knowledge
   - Pass knowledge to Response Agent

## Updated Flow

1. **User submits ticket** → Host Agent
2. **Host Agent** → Ingestion Agent (normalizes ticket)
3. **Ingestion Agent** → Planner Agent (with normalized ticket)
4. **Planner Agent** creates execution plan:
   - Routes to **Intent Classification Agent** (classifies ticket)
   - Routes to **RAG Agent** (retrieves relevant knowledge) ⭐
   - Routes to **Response Agent** (generates response with classification + knowledge)
5. **Response flows back** through Planner → Host → UI

## Testing RAG Integration

### Test RAG Agent Directly

```python
from agents.rag_agent.rag import ChromaRAG

rag = ChromaRAG(
    host="localhost",
    port=8000,
    collection_name="support-agent-x"
)

# Query for relevant documents
results = rag.query("payment issue", n_results=3)
print(results)

# Generate response with RAG
response = rag.generate_response("what are the operating hours?")
print(response)
```

### Test via Planner Agent

1. Submit a ticket: "What are the operating hours?"
2. Planner should route to RAG Agent
3. RAG Agent retrieves: "our operating hours are between 12am to 4pm"
4. Response Agent generates final answer with this context

## Troubleshooting

### RAG Agent not found

- Check RAG Agent is running: `python -m agents.rag_agent.__main__`
- Verify port 10012 is accessible
- Check `RAG_AGENT_URL` environment variable

### ChromaDB connection errors

- Verify ChromaDB server is running
- Check `CHROMA_HOST` and `CHROMA_PORT` environment variables
- Ensure data was ingested: `python scripts/ingest_rag_data.py`

### No documents retrieved

- Verify documents were added to ChromaDB
- Check collection name matches: `CHROMA_COLLECTION=support-agent-x`
- Test ChromaDB connection directly

## Success Criteria

- ✅ Planner Agent discovers RAG Agent at startup
- ✅ Planner Agent routes queries to RAG Agent
- ✅ RAG Agent retrieves relevant documents from ChromaDB
- ✅ Response Agent receives both classification and retrieved knowledge
- ✅ Final response includes context from RAG retrieval
