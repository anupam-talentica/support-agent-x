# Simplified Implementation Task List

## Goal: Minimal Working End-to-End Demo

**Flow:** UI Input → Ingestion Agent → Planner Agent → Response Agent → Output

**Estimated Time:** 3-4 hours  
**Estimated Tokens:** 45,000-69,000  
**Recommended Model:** Composer (Auto mode)

---

## Task 1: Ingestion Agent (1 hour)

### Files to Create:
- `agents/ingestion_agent/ingestion_agent.py`
- `agents/ingestion_agent/ingestion_executor.py`
- `agents/ingestion_agent/__main__.py`

### Implementation Steps:

1. **Create `ingestion_agent.py`**:
   - Use Google ADK `LlmAgent`
   - Reference: `a2a-samples/samples/python/agents/airbnb_planner_multiagent/weather_agent/weather_agent.py`
   - System instruction: "You are a ticket ingestion agent. Normalize user input and extract: title, description, priority (P0-P4), error codes, timestamps."
   - No tools needed (just LLM processing)
   - Output: Structured JSON with extracted fields

2. **Create `ingestion_executor.py`**:
   - Copy from `a2a-samples/samples/python/agents/airbnb_planner_multiagent/weather_agent/weather_executor.py`
   - Rename: `WeatherExecutor` → `IngestionExecutor`
   - Add database integration:
     - Import `TicketService` from `database.services`
     - In `_process_request`, after getting final response, create ticket:
       ```python
       with get_db() as db:
           ticket = TicketService.create_ticket(
               db, user_id='default_user', 
               title=extracted_title, 
               description=extracted_description,
               priority=extracted_priority
           )
       ```

3. **Create `__main__.py`**:
   - Copy from `a2a-samples/samples/python/agents/airbnb_planner_multiagent/weather_agent/__main__.py`
   - Port: 10001
   - AgentCard: name='Ingestion Agent', description='Normalizes and extracts ticket information'
   - Skill: id='ticket_ingestion', examples=['Payment service failing', 'Dashboard not loading']

### Test:
```bash
python -m agents.ingestion_agent.__main__
curl http://localhost:10001/card
```

---

## Task 2: Response Synthesis Agent (1 hour)

### Files to Create:
- `agents/response_agent/response_agent.py`
- `agents/response_agent/response_executor.py`
- `agents/response_agent/__main__.py`

### Implementation Steps:

1. **Create `response_agent.py`**:
   - Use Google ADK `LlmAgent`
   - System instruction: "You are a response synthesis agent. Take the processed ticket information and generate a helpful, professional support response in Markdown format. Include: summary, details, and next steps."
   - No tools needed
   - Input: Structured data from Ingestion Agent
   - Output: Formatted Markdown response

2. **Create `response_executor.py`**:
   - Copy from `weather_executor.py`
   - Rename: `WeatherExecutor` → `ResponseExecutor`
   - Add database integration:
     - Update task with output_data when response is complete

3. **Create `__main__.py`**:
   - Port: 10007
   - AgentCard: name='Response Agent', description='Synthesizes human-readable support responses'
   - Skill: id='response_synthesis', examples=['Format support response', 'Generate help text']

### Test:
```bash
python -m agents.response_agent.__main__
curl http://localhost:10007/card
```

---

## Task 3: Planner/Routing Agent (1.5 hours)

### Files to Create:
- `agents/host_agent/host_agent.py`
- `agents/host_agent/host_executor.py`
- `agents/host_agent/__main__.py`
- `agents/host_agent/remote_agent_connection.py`

### Implementation Steps:

1. **Create `remote_agent_connection.py`**:
   - Copy from `a2a-samples/samples/python/hosts/a2a_multiagent_host/remote_agent_connection.py`
   - This handles A2A client connections

2. **Create `host_agent.py`**:
   - Copy from `a2a-samples/samples/python/hosts/a2a_multiagent_host/routing_agent.py`
   - Simplify routing logic:
     - Remove complex agent selection
     - Simple flow: Always route to Ingestion → Response
   - Update `send_message` tool to route to Ingestion and Response agents
   - System instruction: "You are a routing agent. Route tickets to Ingestion Agent first, then to Response Agent. Always follow this sequence: Ingestion → Response."

3. **Create `host_executor.py`**:
   - Similar to other executors
   - Add database integration:
     - Create task when request comes in
     - Update task status throughout execution
     - Log agent executions

4. **Create `__main__.py`**:
   - Port: 8083
   - Initialize with agent URLs:
     - `INGESTION_AGENT_URL=http://localhost:10001`
     - `RESPONSE_AGENT_URL=http://localhost:10007`
   - AgentCard: name='Host Agent', description='Routes tickets through support agents'

### Test:
```bash
python -m agents.host_agent.__main__
# Test routing
curl -X POST http://localhost:8083/send_message \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"type":"text","text":"Payment failing"}],"messageId":"test123"}}'
```

---

## Task 4: Basic UI (0.5 hours)

### Files to Create:
- `ui/main.py`
- `ui/pages/support_chat.py`
- `ui/components/ticket_form.py`

### Implementation Steps:

1. **Create `ui/main.py`**:
   - Copy from `a2a-samples/demo/ui/main.py`
   - Simplify: Remove agent list management
   - Connect to Host Agent at `http://localhost:8083`

2. **Create `ui/pages/support_chat.py`**:
   - Copy from `a2a-samples/demo/ui/pages/conversation.py`
   - Add ticket form component
   - Display agent execution steps
   - Show final response

3. **Create `ui/components/ticket_form.py`**:
   - Simple form: title, description, priority dropdown
   - Submit button sends to Host Agent

### Test:
```bash
python -m ui.main
# Open http://localhost:12000
```

---

## Task 5: Integration & Testing (0.5 hours)

### Steps:

1. **Start all agents**:
   ```bash
   # Terminal 1
   python -m agents.ingestion_agent.__main__
   
   # Terminal 2
   python -m agents.response_agent.__main__
   
   # Terminal 3
   python -m agents.host_agent.__main__
   
   # Terminal 4
   python -m ui.main
   ```

2. **Test end-to-end**:
   - Open UI: http://localhost:12000
   - Submit ticket: "Payment service failing for EU users"
   - Verify flow: Ingestion → Response
   - Check database: Ticket created, task logged, executions recorded

3. **Verify database**:
   ```python
   from database.connection import get_db
   from database.services import TicketService, TaskService
   
   with get_db() as db:
       tickets = TicketService.list_tickets(db)
       print(f"Tickets: {len(tickets)}")
   ```

---

## File Structure Summary

```
support_agents/
├── agents/
│   ├── ingestion_agent/
│   │   ├── __init__.py
│   │   ├── __main__.py          ← Create (port 10001)
│   │   ├── ingestion_agent.py   ← Create
│   │   └── ingestion_executor.py ← Create
│   ├── response_agent/
│   │   ├── __init__.py
│   │   ├── __main__.py          ← Create (port 10007)
│   │   ├── response_agent.py    ← Create
│   │   └── response_executor.py ← Create
│   └── host_agent/
│       ├── __init__.py
│       ├── __main__.py                    ← Create (port 8083)
│       ├── host_agent.py                  ← Create
│       ├── host_executor.py               ← Create
│       └── remote_agent_connection.py     ← Create
└── ui/
    ├── main.py                  ← Create
    ├── pages/
    │   └── support_chat.py      ← Create
    └── components/
        └── ticket_form.py      ← Create
```

---

## Key Code Patterns

### Agent Creation Pattern:
```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

def create_agent() -> LlmAgent:
    return LlmAgent(
        model=LiteLlm(model='gemini-2.5-flash'),
        name='agent_name',
        description='Agent description',
        instruction="""System instructions...""",
        tools=[],  # No tools for simple agents
    )
```

### Executor Pattern:
```python
from a2a.server.agent_execution import AgentExecutor
from google.adk import Runner
from database.connection import get_db
from database.services import TicketService

class AgentExecutor(AgentExecutor):
    def __init__(self, runner: Runner, card: AgentCard):
        self.runner = runner
        self._card = card
    
    async def execute(self, context, event_queue):
        # Standard ADK execution
        # Add database calls as needed
```

### A2A Server Pattern:
```python
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler

agent_card = AgentCard(
    name='Agent Name',
    description='Description',
    url=f'http://localhost:{PORT}',
    skills=[AgentSkill(...)],
)

executor = AgentExecutor(runner, agent_card)
handler = DefaultRequestHandler(executor=executor, task_store=InMemoryTaskStore())
app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
uvicorn.run(app.build(), host='0.0.0.0', port=PORT)
```

---

## Dependencies Check

Ensure these are in `pyproject.toml`:
- `a2a-sdk>=0.3.0`
- `google-adk>=1.7.0`
- `sqlalchemy>=2.0.0`
- `psycopg2-binary>=2.9.9`
- `uvicorn>=0.27.0`
- `mesop>=0.1.0`
- `httpx>=0.27.0`
- `python-dotenv>=1.0.0`

---

## Environment Variables

Add to `.env`:
```bash
DATABASE_URL=postgresql://support_user:support_pass@localhost:5432/support_agents_db
GOOGLE_API_KEY=your_key_here
INGESTION_AGENT_URL=http://localhost:10001
RESPONSE_AGENT_URL=http://localhost:10007
```

---

## Success Criteria

✅ All 3 agents start without errors  
✅ Host Agent discovers Ingestion and Response agents  
✅ UI can submit tickets  
✅ Tickets flow: UI → Host → Ingestion → Response → UI  
✅ Database shows: ticket created, task logged, executions recorded  
✅ Response is formatted and displayed in UI  

---

## Next Steps (After This Works)

Once this minimal flow works:
- Dev 1: Add RAG Agent → Planner routes to RAG → Response uses retrieved context
- Dev 2: Add Memory Agent → Planner routes to Memory → Response includes historical context
- Dev 3: Add Guardrails Agent → Final safety check before response

---

## Troubleshooting

**Agent not discovered:**
- Check agent is running: `curl http://localhost:PORT/card`
- Verify URL in Host Agent initialization
- Check logs for connection errors

**Database errors:**
- Ensure PostgreSQL is running: `docker-compose ps`
- Run: `python scripts/init_db.py --seed`
- Check DATABASE_URL in .env

**UI not connecting:**
- Verify Host Agent is running on port 8083
- Check browser console for errors
- Verify CORS settings if needed
