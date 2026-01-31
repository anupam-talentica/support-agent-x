"""Planner Agent - Creates execution plans and routes tasks to appropriate agents."""

import asyncio
import logging
import os
import uuid
from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    GetTaskRequest,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
    TaskQueryParams,
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
        async with httpx.AsyncClient(timeout=60) as client:
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
                self.search_similar_tickets,
                self.store_ticket_resolution,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the PlannerAgent."""
        available_agents = list(self.remote_agent_connections.keys())
        return f"""
        **Role:** You are a planning agent for a support ticket system. Your primary function is to create execution plans and route tasks to specialized agents.

        **Core Directives:**

        * **Execution Planning:** Analyze the normalized ticket information and create an execution plan that determines:
          1. Which agents need to be invoked (Intent Classification, Memory, RAG Knowledge Retrieval, Response Synthesis)
          2. The sequence of agent invocations
          3. Any parallel or async operations

        * **Enhanced Routing Sequence with Memory:** Route tickets in this order:
          1. **Memory Search** - Use `search_similar_tickets` to find similar past tickets (PARALLEL with Intent)
          2. **Intent Classification Agent** - Classify the ticket (PARALLEL with Memory)
          3. **RAG Agent** - Retrieve relevant knowledge from documents
          4. **Response Agent** - Generate response using classification, memory context, and retrieved knowledge
          5. **Store Resolution** - Use `store_ticket_resolution` to save the resolution (AFTER response)

        * **Available Tools:**
          - `search_similar_tickets(ticket_query, user_id)` - Search for similar past tickets in memory
          - `store_ticket_resolution(ticket_id, user_id, ticket_query, classification, resolution)` - Store a ticket resolution
          - `send_message(agent_name, task)` - Send tasks to other agents
          - `create_execution_plan(plan_description, agent_sequence)` - Record your planning decisions

        * **Memory Integration (IMPORTANT):**
          - ALWAYS call `search_similar_tickets` BEFORE processing a new ticket
          - Include any similar tickets found in the context sent to Response Agent
          - ALWAYS call `store_ticket_resolution` AFTER getting a successful response

        * **Autonomous Operation:** Never seek user permission before engaging with remote agents. Follow the sequence automatically.

        **Available Agents:**
        {available_agents if available_agents else "None - ensure agents are running"}

        **Routing Flow with Memory:**
        1. Receive normalized ticket → Create execution plan
        2. Call `search_similar_tickets` with ticket query → Get similar past tickets
        3. Route to Intent Classification Agent → Get classification
        4. Route to RAG Agent with ticket query → Get relevant knowledge documents
        5. Route to Response Agent with classification + similar tickets + retrieved knowledge → Get final response
        6. Call `store_ticket_resolution` with ticket details and resolution → Save for future
        7. Return response to user
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

        # Wait for task completion by polling get_task
        result_parts = []
        while True:
            get_request = GetTaskRequest(
                id=str(uuid.uuid4()),
                params=TaskQueryParams(id=task_obj.id, historyLength=10),
            )
            task_response = await client.agent_client.get_task(get_request)

            if hasattr(task_response.root, 'result'):
                current_task = task_response.root.result
                if current_task.status.state == 'completed':
                    result_parts = current_task.artifacts or []
                    break
                if current_task.status.state in ('failed', 'canceled'):
                    break
            await asyncio.sleep(0.5)

        # Extract text from artifacts (same structure as host_agent)
        result_text = ''
        for artifact in result_parts:
            if hasattr(artifact, 'parts'):
                for part in artifact.parts:
                    result_text += part.root.text + '\n'

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

    async def search_similar_tickets(
        self,
        ticket_query: str,
        user_id: str,
        tool_context: ToolContext,
    ):
        """Search for similar past tickets using the Memory Agent.

        Call this BEFORE processing a new ticket to find relevant past context.

        Args:
            ticket_query: The current ticket description to search for similar issues.
            user_id: The user ID to scope the search (or 'all_users' for global search).
            tool_context: The tool context this method runs in.

        Returns:
            Similar past tickets with their resolutions if found.
        """
        if 'Memory Agent' not in self.remote_agent_connections:
            logger.warning('Memory Agent not connected - skipping memory search')
            return {'result': 'Memory Agent not available', 'similar_tickets': []}
        
        memory_task = f"Find similar past tickets for this issue: {ticket_query}. User ID: {user_id}"
        result = await self.send_message('Memory Agent', memory_task, tool_context)
        
        logger.info(f'Memory search completed for user {user_id}')
        return result

    async def store_ticket_resolution(
        self,
        ticket_id: str,
        user_id: str,
        ticket_query: str,
        classification: str,
        resolution: str,
        tool_context: ToolContext,
    ):
        """Store a ticket resolution in the Memory Agent for future reference.

        Call this AFTER successfully resolving a ticket to save the resolution.

        Args:
            ticket_id: The ticket ID being resolved.
            user_id: The user ID who submitted the ticket.
            ticket_query: The original ticket description.
            classification: The ticket classification (intent, urgency, etc.).
            resolution: The resolution provided to the user.
            tool_context: The tool context this method runs in.

        Returns:
            Confirmation that the resolution was stored.
        """
        if 'Memory Agent' not in self.remote_agent_connections:
            logger.warning('Memory Agent not connected - skipping resolution storage')
            return {'result': 'Memory Agent not available - resolution not stored'}
        
        memory_task = (
            f"Store this ticket resolution for future reference:\n"
            f"Ticket ID: {ticket_id}\n"
            f"User ID: {user_id}\n"
            f"Original Issue: {ticket_query}\n"
            f"Classification: {classification}\n"
            f"Resolution: {resolution}"
        )
        result = await self.send_message('Memory Agent', memory_task, tool_context)
        
        logger.info(f'Stored resolution for ticket {ticket_id}')
        return result
