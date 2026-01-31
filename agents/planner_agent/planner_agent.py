"""Planner Agent - Creates execution plans and routes tasks to appropriate agents."""

import logging
import os
import uuid
from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm

from ..host_agent.remote_agent_connection import RemoteAgentConnections

logger = logging.getLogger(__name__)


class PlannerAgent:
    """The Planner agent that creates execution plans and routes tasks."""

    def __init__(self):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}

    async def _async_init_components(
        self, remote_agent_addresses: list[str]
    ) -> None:
        """Asynchronously initialize connections to remote agents."""
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    logger.info(f'Connected to agent: {card.name} at {address}')
                except httpx.ConnectError as e:
                    logger.error(
                        f'ERROR: Failed to connect to agent at {address}: {e}. '
                        f'Make sure the agent is running before starting the Planner Agent.'
                    )
                except Exception as e:
                    logger.error(
                        f'ERROR: Failed to initialize connection for {address}: {e}'
                    )

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
    ) -> 'PlannerAgent':
        """Create and asynchronously initialize an instance of the PlannerAgent."""
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the PlannerAgent."""
        # Use OpenAI model for consistency, or Google AI Studio format
        model_name = os.getenv('LITELLM_MODEL', 'openai/gpt-4.1-mini')
        return Agent(
            model=LiteLlm(model=model_name),
            name='Planner_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This Planner agent creates execution plans and routes tasks to specialized agents'
            ),
            tools=[
                self.send_message,
                self.create_execution_plan,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the PlannerAgent."""
        available_agents = list(self.remote_agent_connections.keys())
        return f"""
        **Role:** You are a planning agent for a support ticket system. Your primary function is to create execution plans and route tasks to specialized agents.

        **Core Directives:**

        * **Execution Planning:** Analyze the normalized ticket information and create an execution plan that determines:
          1. Which agents need to be invoked (Intent Classification, RAG Knowledge Retrieval, Response Synthesis)
          2. The sequence of agent invocations
          3. Any parallel or async operations

        * **Fixed Routing Sequence:** Always route tickets in this exact order:
          1. First, send the ticket to the "Intent Classification Agent" for classification
          2. Then, send the ticket query to the "RAG Agent" to retrieve relevant knowledge from documents
          3. Finally, send the classified ticket information and retrieved knowledge to the "Response Agent" to generate a human-readable response

        * **Task Delegation:** Utilize the `send_message` function to send tasks to remote agents. Always use the exact agent names.

        * **Execution Plan Creation:** Use the `create_execution_plan` function to record your planning decisions.

        * **Autonomous Operation:** Never seek user permission before engaging with remote agents. Follow the sequence automatically.

        **Available Agents:**
        {available_agents if available_agents else "None - ensure agents are running"}

        **Routing Flow:**
        1. Receive normalized ticket → Create execution plan
        2. Route to Intent Classification Agent → Get classification
        3. Route to RAG Agent with ticket query → Get relevant knowledge documents
        4. Route to Response Agent with classification + retrieved knowledge → Get final response
        5. Return aggregated response
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

        Returns:
            A dictionary with the result from the remote agent.
        """
        if agent_name not in self.remote_agent_connections:
            available_agents = list(self.remote_agent_connections.keys())
            error_msg = (
                f'Agent "{agent_name}" not found. '
                f'Available agents: {available_agents if available_agents else "none"}. '
                f'Make sure the {agent_name} is running and accessible before starting the Planner Agent.'
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        state = tool_context.state
        state['active_agent'] = agent_name
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f'Client not available for {agent_name}')
        
        context_id = state.get('context_id', str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'type': 'text', 'text': task}],
                'messageId': message_id,
            },
        }

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
            return {'result': 'Error: Non-success response from agent'}

        if not isinstance(send_response.root.result, Task):
            logger.error('Received non-task response')
            return {'result': 'Error: Non-task response from agent'}

        task_obj = send_response.root.result

        # Wait for task completion and collect artifacts
        result_parts = []
        async for update in client.agent_client.get_task_updates(task_obj.id):
            if update.root.type == 'task_artifact_update':
                if hasattr(update.root, 'artifact') and update.root.artifact:
                    result_parts.append(update.root.artifact)
            elif update.root.type == 'task_status_update':
                if hasattr(update.root, 'status') and update.root.status == 'completed':
                    break

        # Extract text from artifacts
        result_text = ''
        for artifact in result_parts:
            if hasattr(artifact, 'parts'):
                for part in artifact.parts:
                    if part.type == 'text':
                        result_text += part.text + '\n'

        return {'result': result_text if result_text else 'Task completed'}

    async def create_execution_plan(
        self,
        plan_description: str,
        agent_sequence: str,
        tool_context: ToolContext,
    ):
        """Creates an execution plan and stores it in the task metadata.

        Args:
            plan_description: Description of the execution plan.
            agent_sequence: The sequence of agents to be invoked.
            tool_context: The tool context this method runs in.

        Returns:
            A dictionary confirming the plan was created.
        """
        state = tool_context.state
        state['execution_plan'] = {
            'description': plan_description,
            'agent_sequence': agent_sequence,
        }
        logger.info(f'Created execution plan: {plan_description}')
        return {
            'result': f'Execution plan created: {plan_description}. Sequence: {agent_sequence}'
        }
