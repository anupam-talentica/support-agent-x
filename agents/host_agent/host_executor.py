"""Host Agent Executor - A2A bridge for host agent."""

import asyncio
import logging

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
from database.services import TaskService
from google.adk import Runner
from google.genai import types


if TYPE_CHECKING:
    from google.adk.sessions.session import Session


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
DEFAULT_USER_ID = 'self'


class HostExecutor(AgentExecutor):
    """An AgentExecutor that runs an ADK-based Agent for host routing."""

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

                    # Update task in database
                    if hasattr(task_updater, 'task_id') and task_updater.task_id:
                        try:
                            with get_db() as db:
                                response_text = ''
                                if parts and isinstance(parts[0].root, TextPart):
                                    response_text = parts[0].root.text
                                
                                TaskService.update_task_status(
                                    db,
                                    task_id=task_updater.task_id,
                                    status='completed',
                                    output_data={'response': response_text},
                                )
                                logger.info(f'Updated task {task_updater.task_id} in database')
                        except Exception as e:
                            logger.error(f'Failed to update task in database: {e}')

                    logger.debug('#### Yielding final response: %s', parts)
                    await task_updater.add_artifact(parts)

                    await task_updater.update_status(
                        TaskState.completed, final=True
                    )

                    break
                if not event.get_function_calls():
                    parts = [
                        convert_genai_part_to_a2a(part)
                        for part in event.content.parts
                        if (part.text or part.file_data or part.inline_data)
                    ]

                    logger.debug('#### Yielding update response: %s', parts)
                    await task_updater.update_status(
                        TaskState.working,
                        message=task_updater.new_agent_message(parts),
                    )
                else:
                    logger.debug('#### Event - Function Calls')

        finally:
            # Remove from active sessions when done
            self._active_sessions.discard(session_id)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        logger.debug('[host_agent] execute called with context: %s', context)
        
        # Create task in database
        try:
            with get_db() as db:
                task = TaskService.create_task(
                    db,
                    context_id=context.context_id,
                    agent_name='Host Agent',
                    input_data={'message': str(context.message.parts)},
                )
                logger.info(f'Created task in database: {task.task_id}')
        except Exception as e:
            logger.error(f'Failed to create task in database: {e}')

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
        logger.debug('[host_agent] execute exiting')

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the execution for the given context."""
        session_id = context.context_id
        if session_id in self._active_sessions:
            logger.info(
                f'Cancellation requested for active host_agent session: {session_id}'
            )
            self._active_sessions.discard(session_id)
        else:
            logger.debug(
                f'Cancellation requested for inactive host_agent session: {session_id}'
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


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """Convert a single Google Gen AI Part type into an A2A Part type."""
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
