"""Host Agent A2A Server Entry Point with REST API endpoints."""

import asyncio
import logging
import os

import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from .host_agent import HostAgent
from .host_executor import HostExecutor
from .observability import log_status as log_langfuse_status
from .server import get_api_router, set_dependencies


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8083


def _get_initialized_host_agent_sync():
    """Synchronously creates and initializes the HostAgent."""

    async def _async_main():
        host_agent_instance = await HostAgent.create(
            remote_agent_addresses=[
                os.getenv('INGESTION_AGENT_URL', 'http://localhost:10001'),
                os.getenv('PLANNER_AGENT_URL', 'http://localhost:10002'),
                os.getenv('MEMORY_AGENT_URL', 'http://localhost:10005'),
                os.getenv('RESPONSE_AGENT_URL', 'http://localhost:10007'),
            ]
        )
        return host_agent_instance

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            logging.warning(
                'Warning: Could not initialize HostAgent with asyncio.run(): %s. '
                'This can happen if an event loop is already running (e.g., in Jupyter). '
                'Consider initializing HostAgent within an async function in your application.',
                e,
            )
        raise


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the Host Agent server with both A2A and REST API support."""
    
    # Verify an API key is set.

    if os.getenv('GOOGLE_GENAI_USE_VERTEXAI') != 'TRUE' and not os.getenv(
        'GOOGLE_API_KEY'
    ):
        raise ValueError(
            'GOOGLE_API_KEY environment variable not set and '
            'GOOGLE_GENAI_USE_VERTEXAI is not TRUE.'
        )

    # Define agent skill

    skill = AgentSkill(
        id='host_routing',
        name='Host Routing',
        description='Routes tickets through support agents',
        tags=['routing', 'orchestration'],
        examples=[
            'Route ticket to ingestion',
            'Process support ticket',
        ],
    )

    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')

    # Create agent card
    agent_card = AgentCard(
        name='Host Agent',
        description='Routes tickets through support agents',
        url=app_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Initialize the host agent
    host_agent_instance = _get_initialized_host_agent_sync()
    
    # Create shared session service for both A2A and REST API
    session_service = InMemorySessionService()
    
    # Create the ADK agent from host agent
    root_agent = host_agent_instance.create_agent()
    
    # Create runner for the agent
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=session_service,
        memory_service=InMemoryMemoryService(),
    )
    
    # Set dependencies for REST API endpoints
    set_dependencies(host_agent_instance, runner, session_service)
    
    # Create executor for A2A protocol
    agent_executor = HostExecutor(runner, agent_card)

    # Create A2A request handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    # Create A2A application
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    # Build the A2A Starlette app
    a2a_starlette = a2a_app.build()

    # Use FastAPI as main app so /api/* routes are native (fixes 404 when frontend runs outside Docker).
    main_app = FastAPI(title="Host Agent", version="1.0.0")
    main_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @main_app.get("/health")
    async def health_handler():
        agents_count = len(host_agent_instance.cards) if host_agent_instance else 0
        agent_names = list(host_agent_instance.cards.keys()) if host_agent_instance else []
        return JSONResponse({
            "status": "ok",
            "agents_connected": agents_count,
            "agents": agent_names,
        })

    _FAVICON_SVG = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">'
        '<rect width="32" height="32" rx="6" fill="#1e293b"/>'
        '<path d="M8 8l7 8-7 8h3l5.5-6L22 24h3l-7-8 7-8h-3l-5.5 6L11 8H8z" fill="#facc15"/>'
        '<circle cx="22" cy="10" r="2.5" fill="#facc15" opacity="0.95"/>'
        '</svg>'
    )

    @main_app.get("/favicon.ico")
    async def favicon_handler():
        return Response(content=_FAVICON_SVG, media_type="image/svg+xml")

    main_app.include_router(get_api_router(), prefix="/api")
    main_app.mount("/", a2a_starlette)

    # Log startup information (and init Langfuse so status appears in logs)
    log_langfuse_status()
    logger.info(f"Starting Host Agent server on {host}:{port}")
    logger.info(f"  - REST API: http://{host}:{port}/api/chat")
    logger.info(f"  - SSE Stream: http://{host}:{port}/api/chat/stream")
    logger.info(f"  - Agents List: http://{host}:{port}/api/agents")
    logger.info(f"  - A2A Protocol: http://{host}:{port}/")
    logger.info(f"  - Health Check: http://{host}:{port}/health")

    uvicorn.run(main_app, host=host, port=port)


@click.command()
@click.option('--host', 'host', default=DEFAULT_HOST)
@click.option('--port', 'port', default=DEFAULT_PORT)
def cli(host: str, port: int):
    main(host, port)


if __name__ == '__main__':
    main()
