"""Guardrails Agent A2A Server Entry Point."""

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

from .guardrails_agent import create_guardrails_agent
from .guardrails_executor import GuardrailsExecutor


load_dotenv()

logging.basicConfig()

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10008


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    # Guardrails agent uses LiteLlm(LITELLM_MODEL); ensure an API key is set for that model.
    # E.g. OPENAI_API_KEY for openai/gpt-4.1-mini, or GOOGLE_API_KEY for google models.
    lite_model = os.getenv('LITELLM_MODEL', 'openai/gpt-4.1-mini')
    if lite_model.startswith('openai/'):
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError(
                'LITELLM_MODEL is set to an OpenAI model; OPENAI_API_KEY must be set.'
            )
    elif lite_model.startswith('google/') or 'gemini' in lite_model.lower():
        if os.getenv('GOOGLE_GENAI_USE_VERTEXAI') != 'TRUE' and not os.getenv(
            'GOOGLE_API_KEY'
        ):
            raise ValueError(
                'Google model selected; set GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI=TRUE.'
            )

    skill = AgentSkill(
        id='guardrails_policy',
        name='Guardrails & Policy',
        description='Applies safety rules and confidence-based escalation',
        tags=['safety', 'policy', 'escalation'],
        examples=[
            'Review response for safety',
            'Check confidence and escalate if needed',
        ],
    )

    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')

    agent_card = AgentCard(
        name='Guardrails Agent',
        description='Applies safety rules and confidence-based escalation before final response',
        url=app_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    adk_agent = create_guardrails_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    agent_executor = GuardrailsExecutor(runner, agent_card)

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
