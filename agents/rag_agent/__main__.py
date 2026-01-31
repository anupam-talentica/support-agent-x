import logging
import os

import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv

from .agent import RagAgent
from .agent_executor import RagAgentExecutor



load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=10012)
def main(host, port):
    try:
        capabilities = AgentCapabilities(
            streaming=True,
        )
        skill = AgentSkill(
            id='rag_agent',
            name='Rag Agent Tool',
            description='Helps with RAG communication.',
            tags=['RAG'],
            examples=[
                'what is the SLA for dashboards'
            ],
        )
        agent_card = AgentCard(
            name='RAG Agent',
            description='This agent handles RAG activity',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            default_input_modes=RagAgent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=RagAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        agent_executor = RagAgentExecutor()
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
