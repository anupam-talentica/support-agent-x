"""Intent Classification Agent Executor - A2A bridge for intent agent."""

import json
import logging
import re

from typing import TYPE_CHECKING

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    AgentCard,
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from database.connection import get_db
from database.services import TicketService
from google.adk import Runner
from google.genai import types


if TYPE_CHECKING:
    from google.adk.sessions.session import Session


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
DEFAULT_USER_ID = 'self'


class IntentExecutor(AgentExecutor):
    """An AgentExecutor that runs an ADK-based Agent for intent classification."""

    def __init__(self, runner: Runner, card: AgentCard):
        self.runner = runner
        self._card = card
        # Track active sessions for potential cancellation
        self._active_sessions: set[str] = set()

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id

        # Track this session as active
        self._active_sessions.add(session_id)

        try:
            async for event in self.runner.run_async(
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
                new_message=new_message,
            ):
                logger.debug(
                    '### Event received: %s',
                    event.model_dump_json(exclude_none=True, indent=2),
                )

                if event.is_final_response():
                    parts = [
                        convert_genai_part_to_a2a(part)
                        for part in event.content.parts
                        if (part.text or part.file_data or part.inline_data)
                    ]
                    logger.debug('Yielding final response: %s', parts)
                    
                    # Extract classification from response and update ticket in database
                    # Note: convert_genai_part_to_a2a returns TextPart directly for text (not Part(root=TextPart))
                    if parts and isinstance(parts[0], TextPart):
                        response_text = parts[0].text
                        try:
                            # Try to parse JSON from response
                            classification = self._extract_classification(response_text)
                            
                            # Update ticket priority in database if ticket_id is available
                            # Try to extract ticket_id from context or message
                            ticket_id = None
                            try:
                                # Check if we can get ticket_id from task context
                                # This would need to be passed from the planner or host agent
                                # For now, we'll try to find the most recent ticket
                                with get_db() as db:
                                    tickets = TicketService.list_tickets(db, limit=1)
                                    if tickets:
                                        ticket_id = tickets[0].ticket_id
                                        # Update ticket priority
                                        if classification.get('urgency'):
                                            TicketService.update_ticket_priority(
                                                db,
                                                ticket_id=ticket_id,
                                                priority=classification['urgency'],
                                            )
                                            logger.info(
                                                f'Updated ticket {ticket_id} priority to {classification["urgency"]}'
                                            )
                            except Exception as e:
                                logger.error(f'Failed to update ticket priority in database: {e}')
                                # Continue even if DB update fails
                            
                            # Create a new TextPart with updated text (TextPart may be immutable)
                            classification_text = json.dumps(classification, indent=2)
                            parts[0] = TextPart(text=f"{response_text}\n\nClassification:\n{classification_text}")
                        except Exception as e:
                            logger.error(f'Failed to extract classification: {e}')
                            # Continue with original response
                    
                    await task_updater.add_artifact(parts)
                    await task_updater.update_status(
                        TaskState.completed, final=True
                    )
                    break
                if not event.get_function_calls():
                    logger.debug('Yielding update response')
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(
                            [
                                convert_genai_part_to_a2a(part)
                                for part in event.content.parts
                                if (
                                    part.text
                                    or part.file_data
                                    or part.inline_data
                                )
                            ],
                        ),
                    )
                else:
                    logger.debug('Skipping event')
        finally:
            # Remove from active sessions when done
            self._active_sessions.discard(session_id)

    def _extract_classification(self, response_text: str) -> dict:
        """Extract classification data from LLM response text."""
        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                classification = json.loads(json_match.group())
                # Validate classification structure
                if 'incident_type' in classification and 'urgency' in classification:
                    return classification
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract basic info from text
        incident_types = ['Payment', 'API', 'Dashboard', 'Auth', 'Network', 'Other']
        urgency_levels = ['P0', 'P1', 'P2', 'P3', 'P4']
        
        # Try to find incident type
        incident_type = 'Other'
        for itype in incident_types:
            if itype.lower() in response_text.lower():
                incident_type = itype
                break
        
        # Try to find urgency
        urgency = 'P3'  # Default
        for ulevel in urgency_levels:
            if ulevel in response_text:
                urgency = ulevel
                break
        
        # Try to find SLA risk
        sla_risk = 'Medium'  # Default
        if 'high' in response_text.lower() and 'sla' in response_text.lower():
            sla_risk = 'High'
        elif 'low' in response_text.lower() and 'sla' in response_text.lower():
            sla_risk = 'Low'
        
        return {
            'incident_type': incident_type,
            'urgency': urgency,
            'sla_risk': sla_risk,
            'reasoning': 'Extracted from text analysis',
        }

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        # Run the agent until either complete or the task is suspended.
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        # Immediately notify that the task is submitted.
        if not context.current_task:
            await updater.update_status(TaskState.submitted)
        await updater.update_status(TaskState.working)
        await self._process_request(
            types.UserContent(
                parts=[
                    convert_a2a_part_to_genai(part)
                    for part in context.message.parts
                ],
            ),
            context.context_id,
            updater,
        )
        logger.debug('[intent_agent] execute exiting')

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the execution for the given context."""
        session_id = context.context_id
        if session_id in self._active_sessions:
            logger.info(
                f'Cancellation requested for active intent session: {session_id}'
            )
            self._active_sessions.discard(session_id)
        else:
            logger.debug(
                f'Cancellation requested for inactive intent session: {session_id}'
            )

        raise ServerError(error=UnsupportedOperationError())

    async def _upsert_session(self, session_id: str) -> 'Session':
        """Retrieves a session if it exists, otherwise creates a new one."""
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
        )
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
        return session


def convert_a2a_part_to_genai(part: Part) -> types.Part:
    """Convert a single A2A Part type into a Google Gen AI Part type."""
    part = part.root
    if isinstance(part, TextPart):
        return types.Part(text=part.text)
    if isinstance(part, FilePart):
        if isinstance(part.file, FileWithUri):
            return types.Part(
                file_data=types.FileData(
                    file_uri=part.file.uri, mime_type=part.file.mime_type
                )
            )
        if isinstance(part.file, FileWithBytes):
            return types.Part(
                inline_data=types.Blob(
                    data=part.file.bytes, mime_type=part.file.mime_type
                )
            )
        raise ValueError(f'Unsupported file type: {type(part.file)}')
    raise ValueError(f'Unsupported part type: {type(part)}')


def convert_genai_part_to_a2a(part: types.Part):
    """Convert a single Google Gen AI Part type into an A2A Part type."""
    # Note: Returns TextPart/FilePart directly for text/file_data, Part(root=...) for inline_data
    if part.text:
        return TextPart(text=part.text)
    if part.file_data:
        return FilePart(
            file=FileWithUri(
                uri=part.file_data.file_uri,
                mime_type=part.file_data.mime_type,
            )
        )
    if part.inline_data:
        return Part(
            root=FilePart(
                file=FileWithBytes(
                    bytes=part.inline_data.data,
                    mime_type=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f'Unsupported part type: {part}')
