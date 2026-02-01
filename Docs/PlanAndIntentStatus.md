# Implementation Status - Planner and Intent Classification Agents

## Architecture Overview

```mermaid
flowchart TD
    User[User/Support Analyst] --> UI[Mesop UI<br/>Port 12000]
    UI -->|A2A Client| HostAgent[Host Agent<br/>Port 8083<br/>Orchestrator]
    
    HostAgent -->|A2A Protocol| IngestionAgent[Ingestion Agent<br/>Port 10001<br/>Ticket Normalization]
    IngestionAgent -->|A2A Protocol| PlannerAgent[Planner Agent<br/>Port 10002<br/>Task Planning & Routing]
    
    PlannerAgent -->|A2A Protocol| IntentAgent[Intent Classification Agent<br/>Port 10003<br/>Incident Classification]
    PlannerAgent -->|A2A Protocol| ResponseAgent[Response Agent<br/>Port 10007<br/>Response Synthesis]
    
    HostAgent -.->|Create Task| AppDB[(Application Database<br/>PostgreSQL<br/>Tickets, Sessions, Tasks)]
    IngestionAgent -.->|Create Ticket| AppDB
    PlannerAgent -.->|Update Task Plan| AppDB
    IntentAgent -.->|Update Ticket Priority| AppDB
    ResponseAgent -.->|Update Task Status| AppDB
    
    IntentAgent -->|Classification Result| PlannerAgent
    PlannerAgent -->|Planned Sequence| ResponseAgent
    ResponseAgent -->|Response| PlannerAgent
    PlannerAgent -->|Final Response| HostAgent
    HostAgent -->|Final Response| UI
    UI -->|Display| User
    
    style AppDB fill:#e1f5ff
    style HostAgent fill:#fff4e1
    style IngestionAgent fill:#e8f5e9
    style PlannerAgent fill:#ffeb3b
    style IntentAgent fill:#9c27b0
    style ResponseAgent fill:#f3e5f5
    style UI fill:#ffe0e0
```

### Current Implementation Flow

1. **User submits ticket** via Mesop UI (port 12000)
2. **UI sends request** to Host Agent (port 8083) via A2A client
3. **Host Agent orchestrates** the flow:
   - Routes to **Ingestion Agent** (port 10001) for ticket normalization
   - Ingestion Agent creates ticket in PostgreSQL database
   - Routes to **Planner Agent** (port 10002) for task planning
4. **Planner Agent** creates execution plan:
   - Determines which agents need to be invoked
   - Routes to **Intent Classification Agent** (port 10003) for classification
   - Intent Agent classifies incident type, urgency, and updates ticket priority
   - Routes to **Response Agent** (port 10007) for response generation
5. **Response flows back** through Planner → Host → UI
6. **UI displays** the final response to the user

### Database Integration

- **Host Agent**: Creates task records in database
- **Ingestion Agent**: Creates ticket records in database
- **Planner Agent**: Updates task with execution plan metadata
- **Intent Classification Agent**: Updates ticket priority based on classification
- **Response Agent**: Updates task status and output data in database

## ✅ Completed Tasks

### Task 1: Ingestion Agent

- ✅ Created `agents/ingestion_agent/ingestion_agent.py` - LLM agent for ticket normalization
- ✅ Created `agents/ingestion_agent/ingestion_executor.py` - A2A executor with database integration
- ✅ Created `agents/ingestion_agent/__main__.py` - A2A server entry point (port 10001)
- ✅ Integrated with PostgreSQL database to create tickets

### Task 2: Response Agent

- ✅ Created `agents/response_agent/response_agent.py` - LLM agent for response synthesis
- ✅ Created `agents/response_agent/response_executor.py` - A2A executor with database integration
- ✅ Created `agents/response_agent/__main__.py` - A2A server entry point (port 10007)
- ✅ Integrated with database to update task status

### Task 3: Host/Planner Agent

- ✅ Created `agents/host_agent/remote_agent_connection.py` - A2A client wrapper
- ✅ Created `agents/host_agent/host_agent.py` - Routing agent with simplified flow
- ✅ Created `agents/host_agent/host_executor.py` - A2A executor with database integration
- ✅ Created `agents/host_agent/__main__.py` - A2A server entry point (port 8083)
- ✅ Updated routing: Ingestion Agent → Planner Agent

### Task 4: Basic UI

- ✅ Created `ui/main.py` - Simplified Mesop UI for ticket submission
- ✅ Created placeholder files for future expansion
- ✅ Integrated with Host Agent via A2A client

### Task 5: Planner Agent ⭐ NEW

- ✅ Created `agents/planner_agent/planner_agent.py` - ADK agent with planning logic
- ✅ Created `agents/planner_agent/planner_executor.py` - A2A executor with database integration
- ✅ Created `agents/planner_agent/__main__.py` - A2A server entry point (port 10002)
- ✅ Implemented execution plan creation
- ✅ Implemented routing to Intent Classification Agent
- ✅ Implemented routing to Response Agent
- ✅ Integrated with database to store execution plans

### Task 6: Intent Classification Agent ⭐ NEW

- ✅ Created `agents/intent_agent/intent_agent.py` - ADK agent with classification logic
- ✅ Created `agents/intent_agent/intent_executor.py` - A2A executor with database integration
- ✅ Created `agents/intent_agent/__main__.py` - A2A server entry point (port 10003)
- ✅ Implemented incident type classification (Payment, API, Dashboard, Auth, Network, Other)
- ✅ Implemented urgency level classification (P0-P4)
- ✅ Implemented SLA risk assessment (High, Medium, Low)
- ✅ Integrated with database to update ticket priority
- ✅ Added `update_ticket_priority` method to TicketService

## 🏃 Run Locally

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL)
- Google API key

### Step 1: Setup environment

```bash
# From project root
cd support_agents

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On macOS/Linux

# Install dependencies
pip install -e .
```

### Step 2: Configure environment variables

Create `.env` in project root:

```bash
DATABASE_URL=postgresql://support_user:support_pass@localhost:5432/support_agents_db
GOOGLE_API_KEY=your_google_api_key_here
INGESTION_AGENT_URL=http://localhost:10001
PLANNER_AGENT_URL=http://localhost:10002
INTENT_AGENT_URL=http://localhost:10003
RESPONSE_AGENT_URL=http://localhost:10007
HOST_AGENT_URL=http://localhost:8083
```

### Step 3: Start PostgreSQL

```bash
docker-compose up postgres -d
```

### Step 4: Initialize database

```bash
python scripts/init_db.py --seed
```

### Step 5: Start all services (in separate terminals)

Open 7 terminals. In each, activate the venv and run:

| Terminal | Command |
|----------|---------|
| 1 | `source .venv/bin/activate` → `docker-compose up postgres -d` (if not already running) |
| 2 | `source .venv/bin/activate` → `python -m agents.ingestion_agent.__main__` |
| 3 | `source .venv/bin/activate` → `python -m agents.planner_agent.__main__` |
| 4 | `source .venv/bin/activate` → `python -m agents.intent_agent.__main__` |
| 5 | `source .venv/bin/activate` → `python -m agents.response_agent.__main__` |
| 6 | `source .venv/bin/activate` → `python -m agents.host_agent.__main__` |
| 7 | `source .venv/bin/activate` → `gunicorn --bind 0.0.0.0:12000 ui.main:me` |

**Note:** The UI uses Mesop and must be run with gunicorn (not `python -m ui.main`).

**Important:** Start agents in this order:
1. Ingestion Agent (port 10001)
2. Intent Agent (port 10003)
3. Response Agent (port 10007)
4. Planner Agent (port 10002) - connects to Intent and Response
5. Host Agent (port 8083) - connects to Ingestion and Planner
6. UI (port 12000)

### Step 6: Test the flow

- Open UI at http://localhost:12000
- Submit a test ticket (e.g., "Payment service failing for EU users")
- Verify flow: UI → Host → Ingestion → Planner → Intent → Response → Planner → Host → UI
- Check database for:
  - Ticket created with normalized information
  - Ticket priority updated by Intent Agent
  - Task with execution plan from Planner Agent
  - Task status updated by Response Agent

### Verify database

```python
from database.connection import get_db
from database.services import TicketService, TaskService

db_gen = get_db()
db = next(db_gen)
tickets = TicketService.list_tickets(db)
tasks = TaskService.get_tasks_by_context(db, context_id='...')

# Check ticket priority was updated
for ticket in tickets:
    print(f"Ticket {ticket.ticket_id}: Priority {ticket.priority}")

# Check execution plan in task output
for task in tasks:
    if task.output_data and 'execution_plan' in task.output_data:
        print(f"Task {task.task_id} execution plan: {task.output_data['execution_plan']}")
```

## 🔧 Known Issues

1. **Import warnings**: Some linter warnings about missing type stubs for `a2a` and `google.adk` packages - these are expected and don't affect functionality.

2. **Database connection**: The `get_db()` function is a generator, so we need to use `next(db_gen)` instead of `with` statement. This is handled in the code.

3. **UI simplification**: The current UI is very basic. Future enhancements could include:
   - Real-time streaming updates
   - Better error handling
   - Conversation history
   - Agent execution visualization

4. **Ticket ID resolution**: The Intent Agent currently finds the most recent ticket to update priority. In a production system, the ticket_id should be passed through the agent chain.

## 📝 Environment Variables

Ensure these are set in `.env`:

```bash
DATABASE_URL=postgresql://support_user:support_pass@localhost:5432/support_agents_db
GOOGLE_API_KEY=your_key_here
INGESTION_AGENT_URL=http://localhost:10001
PLANNER_AGENT_URL=http://localhost:10002
INTENT_AGENT_URL=http://localhost:10003
RESPONSE_AGENT_URL=http://localhost:10007
HOST_AGENT_URL=http://localhost:8083
```

## 🎯 Success Criteria

- ✅ All 5 agents start without errors
- ✅ Host Agent discovers Ingestion and Planner agents
- ✅ Planner Agent discovers Intent and Response agents
- ✅ UI can submit tickets
- ✅ Tickets flow: UI → Host → Ingestion → Planner → Intent → Response → Planner → Host → UI
- ✅ Database shows: ticket created, priority updated, execution plan stored, task logged
- ✅ Response is formatted and displayed in UI
- ✅ Intent Agent correctly classifies tickets
- ✅ Planner Agent creates execution plans

## 🚀 Future Enhancements

Once the current flow works:

- Dev 1: Add RAG Agent → Planner routes to RAG → Response uses retrieved context
- Dev 2: Add Memory Agent → Planner routes to Memory → Response includes historical context
- Dev 3: Add Guardrails Agent → Final safety check before response
- Dev 4: Add Reasoning Agent → Correlate incidents and provide root cause analysis

## 📊 Agent Summary

| Agent | Port | Status | Purpose |
|-------|------|--------|---------|
| Host Agent | 8083 | ✅ | Main orchestrator, routes to Ingestion and Planner |
| Ingestion Agent | 10001 | ✅ | Normalizes tickets and creates database records |
| Planner Agent | 10002 | ✅ | Creates execution plans and routes to specialized agents |
| Intent Classification Agent | 10003 | ✅ | Classifies tickets by type, urgency, and SLA risk |
| Response Agent | 10007 | ✅ | Generates human-readable responses |

## 🔄 Updated Flow Diagram

The system now supports a more sophisticated routing flow:

1. **Ticket Submission** → Host Agent receives request
2. **Normalization** → Ingestion Agent processes and creates ticket
3. **Planning** → Planner Agent creates execution plan
4. **Classification** → Intent Agent classifies and updates priority
5. **Response Generation** → Response Agent creates final response
6. **Response Delivery** → Response flows back through Planner → Host → UI

This architecture allows for future expansion with additional agents (RAG, Memory, Reasoning, Guardrails) that can be integrated into the Planner's execution plan.
