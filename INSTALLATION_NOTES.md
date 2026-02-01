# Installation Notes

## Basic Installation (Minimal Dependencies)

For the minimal implementation (Ingestion, Response, Host agents + UI):

```bash
pip install -e .
```

This installs only the core dependencies needed for the basic flow.

## RAG Dependencies (Optional)

When you're ready to implement the RAG agent, install RAG dependencies:

```bash
pip install -e ".[rag]"
```

### ChromaDB Installation Issues

**Problem:** `chromadb` requires `onnxruntime>=1.14.1`, which may not have wheels for Python 3.14 on macOS ARM64.

**Workarounds:**

1. **Use Python 3.13 instead of 3.14:**
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[rag]"
   ```

2. **Install chromadb without onnxruntime (if you don't need ONNX features):**
   ```bash
   pip install chromadb --no-deps
   pip install pydantic httpx uvicorn posthog
   ```

3. **Use an alternative vector database:**
   - Consider using `faiss-cpu` or `pinecone` instead of chromadb
   - Or use Google's Vertex AI Vector Search

4. **Wait for onnxruntime Python 3.14 support:**
   - Check: https://pypi.org/project/onnxruntime/
   - Or build from source if needed

## Performance / Why agents feel slow

Each ticket goes through a fixed pipeline: **Host → Ingestion → Planner → Intent → (RAG + Memory in parallel) → Reasoning → Response → store**. That’s several LLM calls and network round-trips, so end-to-end time is dominated by:

- **LLM latency** – Each step (Ingestion, Intent, Reasoning, Response, and each Planner decision) is one or more API calls (often 2–10+ seconds each).
- **Sequential steps** – Planner waits for each sub-agent to finish before the next step (except RAG and Memory, which run in parallel).

**Optimizations applied:**

- **Reasoning agent health check** – Timeout reduced from 10s to 2s so a missing/unreachable health endpoint fails quickly instead of blocking.
- **Task polling** – Planner and Host poll for task completion every 0.25s instead of 0.5s so completion is detected sooner.

**First run:** Memory agent downloads an embedding model (~79MB) on first use; that’s one-time and can add ~30–40s to the first ticket.

**Optional:** To avoid the reasoning health check delay when no health service exists, set `HEALTH_CHECK_URL=` (empty) in `.env` so the agent skips the check, or point it to a real health endpoint.

## Current Status

- ✅ Core dependencies install cleanly
- ⚠️ RAG dependencies may have issues on Python 3.14
- ✅ All minimal implementation dependencies work
