"""Host Agent A2A Server Entry Point."""

import asyncio
import logging
import os

import click
import uvicorn

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


load_dotenv()

logging.basicConfig()

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8083


def _get_initialized_host_agent_sync():
    """Synchronously creates and initializes the HostAgent."""

    async def _async_main():
        host_agent_instance = await HostAgent.create(
            remote_agent_addresses=[
                os.getenv('INGESTION_AGENT_URL', 'http://localhost:10001'),
                os.getenv('RESPONSE_AGENT_URL', 'http://localhost:10007'),
                os.getenv('RAG_AGENT_URL', 'http://localhost:10012'),
            ]
        )
        return host_agent_instance.create_agent()

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
    # Verify an API key is set.
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

    root_agent = _get_initialized_host_agent_sync()
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    agent_executor = HostExecutor(runner, agent_card)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    uvicorn.run(a2a_app.build(), host=host, port=port)


@click.command()
@click.option('--host', 'host', default=DEFAULT_HOST)
@click.option('--port', 'port', default=DEFAULT_PORT)
def cli(host: str, port: int):
    main(host, port)


if __name__ == '__main__':
    main()
