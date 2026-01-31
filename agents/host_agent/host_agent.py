"""Host Agent - Routes tickets through support agents."""

import json
import logging
import os
import uuid

from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from a2a.types import TaskResubscriptionRequest, TaskIdParams
from a2a.types import GetTaskRequest, TaskQueryParams
import asyncio


from .remote_agent_connection import RemoteAgentConnections


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()


def convert_part(part: Part, tool_context: ToolContext):
    """Convert a part to text. Only text parts are supported."""
    if part.type == 'text':
        return part.text
    return f'Unknown type: {part.type}'


def convert_parts(parts: list[Part], tool_context: ToolContext):
    """Convert parts to text."""
    rval = []
    for p in parts:
        rval.append(convert_part(p, tool_context))
    return rval


class HostAgent:
    """The Host agent that routes tickets through support agents.

    This agent orchestrates the flow: Ingestion Agent → Response Agent
    """

    def __init__(self):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

    async def _async_init_components(
        self, remote_agent_addresses: list[str]
    ) -> None:
        """Asynchronously initialize connections to remote agents."""
        failed_connections = []
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                    logger.info(f'Connected to agent: {card.name} at {address}')
                except httpx.ConnectError as e:
                    failed_connections.append(address)
                    logger.error(
                        f'ERROR: Failed to connect to agent at {address}: {e}. '
                        f'Make sure the agent is running before starting the Host Agent.'
                    )
                except Exception as e:
                    failed_connections.append(address)
                    logger.error(
                        f'ERROR: Failed to initialize connection for {address}: {e}'
                    )

        if failed_connections:
            logger.warning(
                f'WARNING: Failed to connect to {len(failed_connections)} agent(s). '
                f'These agents will not be available: {failed_connections}. '
                f'Available agents: {list(self.remote_agent_connections.keys())}'
            )

        # Populate self.agents
        agent_info = []
        for agent_detail_dict in self.list_remote_agents():
            agent_info.append(json.dumps(agent_detail_dict))
        self.agents = '\n'.join(agent_info)

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
    ) -> 'HostAgent':
        """Create and asynchronously initialize an instance of the HostAgent."""
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the HostAgent."""
        gemini_model = "openai/gpt-4.1-mini"
        return Agent(
            model=gemini_model,
            name='Host_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This Host agent orchestrates the routing of support tickets through specialized agents'
            ),
            tools=[
                self.send_message,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the HostAgent."""
        return f"""
        **Role:** You are a routing agent for a support ticket system. Your primary function is to route tickets through the support agent pipeline in a fixed sequence.

        **Core Directives:**

        * **Fixed Routing Sequence:** Always route tickets in this exact order:
          1. First, send the ticket to the "Ingestion Agent" to normalize and extract ticket information
          2. Then, send the processed ticket information to the "Response Agent" to generate a human-readable response

        * **Task Delegation:** Utilize the `send_message` function to send tasks to remote agents. Always use the exact agent names: "Ingestion Agent" and "Response Agent".

        * **Autonomous Operation:** Never seek user permission before engaging with remote agents. Follow the sequence automatically.

        * **Transparent Communication:** Present the complete and detailed response from the final agent (Response Agent) to the user.

        * **Tool Reliance:** Strictly rely on available tools to address user requests. Do not generate responses based on assumptions.

        **Available Agents:**
        {self.agents}

        **Routing Flow:**
        1. User submits ticket → Send to "Ingestion Agent"
        2. Ingestion Agent processes → Send result to "Response Agent"
        3. Response Agent generates response → Return to user
        """

    def before_model_callback(
        self,
        callback_context: CallbackContext,
        llm_request,
    ):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True

    def list_remote_agents(self):
        """List the available remote agents."""
        if not self.cards:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            logger.debug(
                'Found agent card: %s', card.model_dump(exclude_none=True)
            )
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info

    async def send_message(
        self,
        agent_name: str,
        task: str,
        tool_context: ToolContext,
    ):
        """Sends a task to a remote agent.

        Args:
            agent_name: The name of the agent to send the task to.
            task: The task description or ticket information.
            tool_context: The tool context this method runs in.

        Yields:
            A dictionary of JSON data.
        """
        if agent_name not in self.remote_agent_connections:
            available_agents = list(self.remote_agent_connections.keys())
            error_msg = (
                f'Agent "{agent_name}" not found. '
                f'Available agents: {available_agents if available_agents else "none"}. '
                f'Make sure the {agent_name} is running and accessible before starting the Host Agent.'
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        state = tool_context.state
        state['active_agent'] = agent_name
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f'Client not available for {agent_name}')
        
        task_id = state.get('task_id')
        context_id = state.get('context_id', str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'type': 'text', 'text': task}],
                'messageId': message_id,
            },
        }

        if task_id:
            payload['message']['taskId'] = task_id

        if context_id:
            payload['message']['contextId'] = context_id

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(
            message_request=message_request
        )
        logger.debug(
            'send_response: %s',
            send_response.model_dump_json(exclude_none=True, indent=2),
        )

        if not isinstance(send_response.root, SendMessageSuccessResponse):
            logger.error('Received non-success response')
            return None

        if not isinstance(send_response.root.result, Task):
            logger.error('Received non-task response')
            return None

        task = send_response.root.result

        # Wait for task completion and collect artifacts
        result_parts = []
        while True:
            get_request = GetTaskRequest(
                id=str(uuid.uuid4()),
                params=TaskQueryParams(id=task.id, historyLength=10)
            )
            task_response = await client.agent_client.get_task(get_request)
            
            if hasattr(task_response.root, 'result'):
                current_task = task_response.root.result
                if current_task.status.state == 'completed':
                    result_parts = current_task.artifacts or []
                    break
                elif current_task.status.state in ['failed', 'canceled']:
                    break
            await asyncio.sleep(0.5)

        # Extract text from artifacts
        result_text = ''
        for artifact in result_parts:
            if hasattr(artifact, 'parts'):
                for part in artifact.parts:
                    result_text += part.root.text + '\n'

        return {'result': result_text if result_text else 'Task completed'}
