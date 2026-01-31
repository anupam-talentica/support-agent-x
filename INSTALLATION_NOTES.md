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

## Current Status

- ✅ Core dependencies install cleanly
- ⚠️ RAG dependencies may have issues on Python 3.14
- ✅ All minimal implementation dependencies work
