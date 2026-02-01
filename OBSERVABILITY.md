# Host Agent Observability (Langfuse)

The Host Agent uses [Langfuse](https://langfuse.com/docs) for observability so you can see how each request progresses through the orchestrator and which agents were involved.

## What is traced

- **One trace per request** (REST or A2A):
  - **REST** (`POST /api/chat`, `GET /api/chat/stream`): trace name `rest-chat` / `rest-chat-stream`, with `session_id` = `conversation_id`, `user_id` = mobile number when the React UI sends the `X-User-Phone` header (else `api_user`).
  - **A2A** (HostExecutor): trace name `a2a-execute`, with `session_id` = request context ID.
- **One span per agent delegation**: when the Host Agent calls `send_message(agent_name, task)`, a child span is created (e.g. `delegate-to-Ingestion Agent`, `delegate-to-Planner Agent`) with input (task preview) and output (result preview).

So in Langfuse you get:

1. **Trace** = full request (user message → Host Agent → Ingestion → Planner → … → final response).
2. **Spans** = Host Agent processing and each delegation to Ingestion/Planner (and any other remote agents).

Sessions group multiple traces by `session_id` (e.g. one conversation = one session).

## Setup

1. **Get Langfuse credentials**
   - Sign up at [Langfuse Cloud](https://cloud.langfuse.com) or [self-host](https://langfuse.com/docs/self-hosting).
   - Create a project and copy the **Public Key** and **Secret Key**.

2. **Configure environment**
   - **Docker**: Add these to the same `.env` file used by `docker-compose` (in the project root), then restart: `docker compose up -d host_agent`.
   - **Local**: Add to your `.env` or export before starting the Host Agent:

   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   # Optional (default: https://cloud.langfuse.com)
   # LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
   ```

3. **Run the Host Agent**
   - If the keys are set, the agent logs: `Langfuse observability enabled.`
   - If not set, observability is disabled and the app runs as before (no errors).

## Viewing traces

1. Open your Langfuse project (Cloud or self-hosted).
2. Go to **Traces** to see each request.
3. Open a trace to see the tree: root span (e.g. `rest-chat`) and child spans (`delegate-to-Ingestion Agent`, `delegate-to-Planner Agent`, etc.).
4. Use **Sessions** to group by conversation (`session_id` = `conversation_id` for REST).
5. Filter traces by **User** (mobile number): when the React UI is used, the logged-in user's mobile number is sent as `X-User-Phone` and stored as Langfuse `user_id`, so you can filter or search traces by that number in Langfuse.

## Implementation details

- **Module**: `agents/host_agent/observability.py` — lazy Langfuse client, `trace_request()`, `span_agent_call()`, `update_current_span()`, `flush()`.
- **Instrumentation**:
  - `server.py`: REST endpoints wrapped in `trace_request`; output and `flush()` on completion.
  - `host_agent.py`: `send_message()` wrapped in `span_agent_call(agent_name, task)`; result recorded via `update_current_span`.
  - `host_executor.py`: A2A `_process_request()` wrapped in `trace_request`; completion/failure recorded with `update_current_span`.

Inputs/outputs are truncated (e.g. 500–2000 chars) to avoid huge payloads in Langfuse.

## References

- [Langfuse docs](https://langfuse.com/docs)
- [Python SDK – Get started](https://langfuse.com/docs/sdk/python)
- [Instrumentation (context manager, spans)](https://langfuse.com/docs/observability/sdk/instrumentation)
- [Sessions](https://langfuse.com/docs/observability/features/sessions)
