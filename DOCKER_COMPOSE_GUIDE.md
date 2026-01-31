# Docker Compose Quick Start Guide

This guide explains how to run all agents together using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Google API key (for LLM access)

## Quick Start

### 1. Create `.env` file

Create a `.env` file in the `support_agents` directory:

```bash
# Required: Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Vertex AI Configuration (if using Vertex AI instead of API key)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=global

# Optional: LLM Model
LITELLM_MODEL=gemini-2.5-flash
```

### 2. Start all services

```bash
cd support_agents
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Initialize the database with seed data
- Start all 5 agents (Ingestion, Planner, Intent, Response, Host)
- Start the UI

### 3. Access the UI

Open your browser and navigate to:
```
http://localhost:12000
```

### 4. Stop all services

Press `Ctrl+C` in the terminal, or run:
```bash
docker-compose down
```

To also remove volumes (database data):
```bash
docker-compose down -v
```

## Service Details

| Service | Port | Description | Dependencies |
|---------|------|-------------|---------------|
| `postgres` | 5432 | PostgreSQL database | None |
| `ingestion_agent` | 10001 | Ticket normalization | PostgreSQL |
| `intent_agent` | 10003 | Ticket classification | PostgreSQL |
| `response_agent` | 10007 | Response generation | PostgreSQL |
| `planner_agent` | 10002 | Task planning & routing | PostgreSQL, Intent, Response |
| `host_agent` | 8083 | Main orchestrator | PostgreSQL, Ingestion, Planner |
| `ui` | 12000 | Mesop web UI | PostgreSQL, Host Agent |

## Startup Order

The services start in the following order:

1. **PostgreSQL** - Database must be healthy first
2. **Ingestion, Intent, Response Agents** - Start in parallel (only depend on DB)
3. **Planner Agent** - Waits for Intent and Response
4. **Host Agent** - Waits for Ingestion and Planner
5. **UI** - Waits for Host Agent and initializes database

## Viewing Logs

### All services
```bash
docker-compose logs -f
```

### Specific service
```bash
docker-compose logs -f ingestion_agent
docker-compose logs -f planner_agent
docker-compose logs -f host_agent
docker-compose logs -f ui
```

## Restarting a Single Service

```bash
docker-compose restart ingestion_agent
docker-compose restart planner_agent
```

## Rebuilding After Code Changes

```bash
docker-compose up --build
```

## Troubleshooting

### Agents can't connect to each other

- Ensure all services are running: `docker-compose ps`
- Check logs: `docker-compose logs`
- Verify network: All services are on `support_agents_network`

### Database connection errors

- Wait for PostgreSQL to be healthy: `docker-compose ps postgres`
- Check database logs: `docker-compose logs postgres`
- Verify `DATABASE_URL` environment variable

### Agent not found errors

- Check that dependent agents are running before the agent that needs them
- Review startup order in docker-compose.yml
- Check agent URLs in environment variables

### Port conflicts

If ports are already in use, you can:
- Stop conflicting services
- Modify port mappings in docker-compose.yml

## Development Mode

For development, you may want to mount your code as a volume for live reloading:

```yaml
volumes:
  - .:/app
  - ./data:/app/data
```

Note: This is already configured in the docker-compose.yml for the `data` directory.

## Production Considerations

For production use:
1. Use environment-specific `.env` files
2. Set up proper secrets management
3. Configure resource limits for each service
4. Set up health checks and monitoring
5. Use a reverse proxy (nginx/traefik) for the UI
6. Configure proper logging and log aggregation

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Google API key for LLM access |
| `GOOGLE_GENAI_USE_VERTEXAI` | No | `FALSE` | Use Vertex AI instead of API key |
| `GOOGLE_CLOUD_PROJECT` | No | - | GCP project ID (if using Vertex AI) |
| `GOOGLE_CLOUD_LOCATION` | No | `global` | GCP location (if using Vertex AI) |
| `LITELLM_MODEL` | No | `gemini-2.5-flash` | LLM model to use |
| `DATABASE_URL` | Auto | - | Automatically set to PostgreSQL connection |

## Network Architecture

All services communicate over the `support_agents_network` bridge network:

```
┌─────────────┐
│   UI        │ (12000)
└──────┬──────┘
       │
┌──────▼──────┐
│ Host Agent  │ (8083)
└──┬──────────┘
   │
   ├──► Ingestion Agent (10001)
   │
   └──► Planner Agent (10002)
       │
       ├──► Intent Agent (10003)
       │
       └──► Response Agent (10007)
```

All agents connect to PostgreSQL on the same network.
