"""Planner Agent A2A Server Entry Point."""

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

from .planner_agent import PlannerAgent
from .planner_executor import PlannerExecutor


load_dotenv()

logging.basicConfig()

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10002


def _get_initialized_planner_agent_sync():
    """Synchronously creates and initializes the PlannerAgent."""

    async def _async_main():
        planner_agent_instance = await PlannerAgent.create(
            remote_agent_addresses=[
                os.getenv('INTENT_AGENT_URL', 'http://localhost:10003'),
                os.getenv('RESPONSE_AGENT_URL', 'http://localhost:10007'),
            ]
        )
        return planner_agent_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            logging.warning(
                'Warning: Could not initialize PlannerAgent with asyncio.run(): %s. '
                'This can happen if an event loop is already running (e.g., in Jupyter). '
                'Consider initializing PlannerAgent within an async function in your application.',
                e,
            )
        raise


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    # Verify an API key is set.
    if os.getenv('GOOGLE_GENAI_USE_VERTEXAI') != 'TRUE' and not os.getenv(
        'GOOGLE_API_KEY'
    ):
        raise ValueError(
            'GOOGLE_API_KEY environment variable not set and '
            'GOOGLE_GENAI_USE_VERTEXAI is not TRUE.'
        )

    skill = AgentSkill(
        id='task_planning',
        name='Task Planning',
        description='Creates execution plans and routes tasks to specialized agents',
        tags=['planning', 'routing', 'orchestration'],
        examples=[
            'Plan ticket processing workflow',
            'Route to classification agent',
            'Create execution sequence',
        ],
    )

    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')

    agent_card = AgentCard(
        name='Planner Agent',
        description='Creates execution plans and routes tasks to specialized agents',
        url=app_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    root_agent = _get_initialized_planner_agent_sync()
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    agent_executor = PlannerExecutor(runner, agent_card)

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
