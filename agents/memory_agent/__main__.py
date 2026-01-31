"""Memory Agent A2A Server Entry Point."""

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
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .memory_agent import Mem0MemoryAgent
from .memory_tools import MemoryTools


load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 10005


def create_memory_agent() -> LlmAgent:
    """Create the ADK memory agent with mem0 tools."""
    # Initialize mem0 agent and tools
    mem0_agent = Mem0MemoryAgent()
    memory_tools = MemoryTools(mem0_agent)
    
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'openai/gpt-4o-mini')
    
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='memory_agent',
        description='Manages conversational memory using mem0 for intelligent fact extraction and recall',
        instruction="""You are a memory management agent powered by mem0. Your role is to help store and recall important information across user interactions.

**Core Capabilities:**
1. **Store Context**: When important information is mentioned (user preferences, issue patterns, resolutions), store it for future reference
2. **Recall Context**: Search past memories to provide relevant context for current issues
3. **Track Tickets**: Store complete ticket resolutions to help with similar future issues
4. **Find Patterns**: Identify similar past tickets to speed up resolution

**When to Store Memories:**
- User preferences (e.g., "prefers email notifications")
- Common issues for a user
- Successful resolutions
- Important context that might be useful later

**When to Recall Memories:**
- User submits a new ticket (check for past similar issues)
- Need context about a user's history
- Looking for patterns across tickets

**Available Tools:**
- `store_context`: Store important information
- `recall_context`: Search for relevant memories
- `get_user_history`: Get all memories for a user
- `store_ticket_resolution`: Store complete ticket with resolution
- `find_similar_tickets`: Find similar past tickets

Always use these tools to manage memory. Be proactive about storing useful information and recalling relevant context.""",
        tools=[
            memory_tools.store_context,
            memory_tools.recall_context,
            memory_tools.get_user_history,
            memory_tools.store_ticket_resolution,
            memory_tools.find_similar_tickets,
        ],
    )


class MemoryExecutor:
    """Executor wrapper for memory agent (if needed for custom handling)."""
    
    def __init__(self, runner, agent_card):
        self.runner = runner
        self.agent_card = agent_card


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    # Verify API keys
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY environment variable not set (required for mem0)')
    
    skill = AgentSkill(
        id='memory_management',
        name='Memory Management',
        description='Intelligent memory storage and recall using mem0',
        tags=['memory', 'context', 'recall'],
        examples=[
            'Store user preference for email notifications',
            'Recall similar past tickets',
            'Get user interaction history',
        ],
    )

    app_url = os.environ.get('APP_URL', f'http://{host}:{port}')

    agent_card = AgentCard(
        name='Memory Agent',
        description='Manages conversational memory using mem0 for intelligent fact extraction and recall',
        url=app_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    adk_agent = create_memory_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    # Use the default executor or custom MemoryExecutor if needed
    from agents.ingestion_agent.ingestion_executor import IngestionExecutor
    # Using the same pattern as other agents
    agent_executor = IngestionExecutor(runner, agent_card)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    logger.info(f"Starting Memory Agent on {host}:{port}")
    uvicorn.run(a2a_app.build(), host=host, port=port)


@click.command()
@click.option('--host', 'host', default=DEFAULT_HOST)
@click.option('--port', 'port', default=DEFAULT_PORT)
def cli(host: str, port: int):
    main(host, port)


if __name__ == '__main__':
    main()
