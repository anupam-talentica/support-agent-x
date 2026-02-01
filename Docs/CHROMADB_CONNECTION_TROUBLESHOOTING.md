# ChromaDB Connection Troubleshooting

## Issue
RAG agent in Docker cannot connect to ChromaDB running on Mac host at `localhost:8000`.

## Current Configuration
- RAG agent uses `CHROMA_HOST=host.docker.internal`
- ChromaDB should be running on Mac at `localhost:8000`

## Troubleshooting Steps

### 1. Verify ChromaDB is Running
```bash
# On your Mac, test if ChromaDB is accessible
curl http://localhost:8000/api/v1/heartbeat
```

If this fails, ChromaDB is not running or not accessible.

### 2. Check ChromaDB Bind Address
ChromaDB must be listening on `0.0.0.0` (all interfaces), not just `127.0.0.1`.

**If ChromaDB is started with a command like:**
```bash
chroma run --host localhost --port 8000
```

**Change it to:**
```bash
chroma run --host 0.0.0.0 --port 8000
```

This allows Docker containers to connect via `host.docker.internal`.

### 3. Test Connectivity from Docker Container
```bash
# Test from inside the container
docker-compose exec rag_agent curl http://host.docker.internal:8000/api/v1/heartbeat
```

If this fails, there's a network connectivity issue.

### 4. Alternative: Use Your Mac's IP Address
If `host.docker.internal` doesn't work, find your Mac's IP:

```bash
# On Mac, find your IP address
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Then set in `.env` or `docker-compose.yml`:
```bash
CHROMA_HOST=<your-mac-ip-address>
```

### 5. Alternative: Use Network Mode Host (Linux only)
On Linux, you can use:
```yaml
rag_agent:
  network_mode: host
```

**Note:** This doesn't work on Mac/Windows Docker Desktop.

### 6. Verify Environment Variable
```bash
# Check if environment variable is set correctly
docker-compose exec rag_agent env | grep CHROMA
```

Should show:
```
CHROMA_HOST=host.docker.internal
CHROMA_PORT=8000
```

## Solution Summary

**Most likely fix:** Ensure ChromaDB is listening on `0.0.0.0:8000` instead of `127.0.0.1:8000`:

```bash
# Stop ChromaDB if running
# Then restart with:
chroma run --host 0.0.0.0 --port 8000
```

This allows Docker containers to connect via `host.docker.internal`.
