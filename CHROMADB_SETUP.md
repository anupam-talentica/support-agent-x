# ChromaDB Setup Guide

## Quick Start

**Start ChromaDB server:**
```bash
chroma run --host 0.0.0.0 --port 8000
```

**Important:** Always use `--host 0.0.0.0` (not `localhost` or `127.0.0.1`) to allow Docker containers to connect via `host.docker.internal`.

## Why 0.0.0.0?

- `localhost` or `127.0.0.1`: Only accessible from the same machine, Docker containers cannot connect
- `0.0.0.0`: Listens on all network interfaces, allows Docker containers to connect via `host.docker.internal`

## Verification

### Test from your Mac:
```bash
curl http://localhost:8000/api/v1/heartbeat
```

### Test from Docker container:
```bash
docker-compose exec rag_agent curl http://host.docker.internal:8000/api/v1/heartbeat
```

### Check what interface ChromaDB is listening on:
```bash
lsof -i :8000
```

Should show `*:irdmi (LISTEN)` (the `*` means all interfaces), not `localhost:irdmi`.

## Ingest Documents

After ChromaDB is running, ingest documents:

```bash
python scripts/ingest_rag_data.py
```

## Configuration

Set these environment variables in `.env` or `docker-compose.yml`:

```bash
# For Docker (RAG agent in container connecting to host)
CHROMA_HOST=host.docker.internal
CHROMA_PORT=8000
CHROMA_COLLECTION=support-agent-x

# For local development (RAG agent on same machine)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=support-agent-x
```

## Troubleshooting

See `CHROMADB_CONNECTION_TROUBLESHOOTING.md` for detailed troubleshooting steps.

## Common Issues

1. **"Could not connect to a Chroma server"**
   - Solution: Restart ChromaDB with `--host 0.0.0.0`

2. **Connection works from Mac but not from Docker**
   - Solution: Ensure ChromaDB is listening on `0.0.0.0`, not `127.0.0.1`

3. **Port already in use**
   - Solution: Find and stop the existing ChromaDB process, or use a different port
