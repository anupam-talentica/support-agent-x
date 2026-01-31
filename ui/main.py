"""Simplified UI for Support Agents Demo."""

import os
import uuid

import httpx
import mesop as me

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, Part, Role, SendMessageRequest, TextPart

from a2a.types import GetTaskRequest, TaskQueryParams
import asyncio

from dotenv import load_dotenv

from dataclasses import field


load_dotenv()

HOST_AGENT_URL = os.getenv('HOST_AGENT_URL', 'http://localhost:8083')


@me.stateclass
class AppState:
    """Application state"""
    messages: list[dict] = field(default_factory=list)
    loading: bool = False


async def send_ticket(title: str, description: str):
    """Send ticket to host agent."""
    state = me.state(AppState)
    state.loading = True
    yield
    
    try:
        # Get agent card (long timeout: host runs full pipeline before responding)
        async with httpx.AsyncClient(timeout=120) as client:
            card_resolver = A2ACardResolver(client, HOST_AGENT_URL)
            agent_card = await card_resolver.get_agent_card()
            
            # Create A2A client
            a2a_client = A2AClient(client, agent_card, url=HOST_AGENT_URL)
            
            # Create message
            message_text = f"Title: {title}\n\nDescription: {description}"
            message = Message(
                message_id=str(uuid.uuid4()),
                context_id=str(uuid.uuid4()),
                role=Role.user,
                parts=[Part(root=TextPart(text=message_text))],
            )
            
            # Send message
            request = SendMessageRequest(
                id=message.message_id,
                params={
                    'message': {
                        'role': 'user',
                        'parts': [{'type': 'text', 'text': message_text}],
                        'messageId': message.message_id,
                        'contextId': message.context_id,
                    }
                }
            )
            
            response = await a2a_client.send_message(request)
            
            # Server runs the full agent then returns; response may contain completed task (no polling needed)
            result = getattr(response.root, 'result', None)
            current_task = None
            task_id = getattr(result, 'id', None) if result is not None else None
            if result is not None:
                task_state = getattr(getattr(result, 'status', None), 'state', None)
                if task_state == 'completed':
                    current_task = result  # use send_message response directly
            # If not completed, poll get_task until done or timeout
            max_polls = 240  # 2 min at 0.5s
            poll_count = 0

            while current_task is None and task_id and poll_count < max_polls:
                get_request = GetTaskRequest(
                    id=str(uuid.uuid4()),
                    params=TaskQueryParams(id=task_id, historyLength=10)
                )
                task_response = await a2a_client.get_task(get_request)
                poll_count += 1

                if hasattr(task_response.root, 'result') and task_response.root.result is not None:
                    current_task = task_response.root.result
                    task_state = getattr(getattr(current_task, 'status', None), 'state', None)
                    if task_state == 'completed':
                        break
                    if task_state in ('failed', 'canceled'):
                        state.messages.append({
                            'role': 'error',
                            'content': f'Task {task_state}',
                        })
                        yield
                        current_task = None
                        break
                    # Still working; clear so we keep polling
                    current_task = None
                await asyncio.sleep(0.5)

            if poll_count >= max_polls and current_task is None:
                state.messages.append({
                    'role': 'error',
                    'content': 'Task did not complete in time.',
                })
                yield
            elif current_task is not None:
                # Show artifacts from completed task
                artifacts = getattr(current_task, 'artifacts', None) or []
                for artifact in artifacts:
                    if hasattr(artifact, 'parts'):
                        for part in artifact.parts:
                            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                                state.messages.append({
                                    'role': 'assistant',
                                    'content': part.root.text,
                                })
                                yield
            
            # Add user message
            state.messages.insert(0, {
                'role': 'user',
                'content': message_text,
            })
            yield
            
    except Exception as e:
        state.messages.insert(0, {
            'role': 'error',
            'content': f'Error: {str(e)}',
        })
        yield
    finally:
        state.loading = False
        yield


@me.stateclass
class FormState:
    """Form state"""
    title: str = ''
    description: str = ''
    priority: str = 'P3'


async def submit_ticket(e: me.ClickEvent):
    """Submit ticket handler"""
    form_state = me.state(FormState)
    if not form_state.title or not form_state.description:
        return
    
    async for _ in send_ticket(form_state.title, form_state.description):
        yield
    
    # Clear form
    form_state.title = ''
    form_state.description = ''
    form_state.priority = 'P3'


@me.page(path='/', title='Support Agents')
def support_page():
    """Support ticket page"""
    app_state = me.state(AppState)
    form_state = me.state(FormState)
    
    with me.box(style=me.Style(padding=me.Padding.all(20), max_width=1200,margin=me.Margin.symmetric(vertical=0, horizontal='auto'))):
        me.text('Support Ticket System', style=me.Style(font_size=24, font_weight='bold', margin=me.Margin(bottom=20)))
        
        # Ticket form
        with me.box(style=me.Style(
            border=me.Border.all(me.BorderSide(width=1, color='#ccc', style='solid')),
            padding=me.Padding.all(20),
            margin=me.Margin(bottom=20),
            border_radius=8,
        )):
            me.text('Submit a Ticket', style=me.Style(font_size=18, font_weight='bold', margin=me.Margin(bottom=10)))
            
            me.input(
                label='Title',
                value=form_state.title,
                on_input=lambda e: setattr(form_state, 'title', e.value),
                style=me.Style(margin=me.Margin(bottom=10)),
            )
            
            me.textarea(
                label='Description',
                value=form_state.description,
                on_input=lambda e: setattr(form_state, 'description', e.value),
                style=me.Style(margin=me.Margin(bottom=10), min_height=100),
            )
            
            me.select(
                label='Priority',
                options=[
                    me.SelectOption(label='P0 - Critical', value='P0'),
                    me.SelectOption(label='P1 - High', value='P1'),
                    me.SelectOption(label='P2 - Medium', value='P2'),
                    me.SelectOption(label='P3 - Low', value='P3'),
                    me.SelectOption(label='P4 - Lowest', value='P4'),
                ],
                value=form_state.priority,
                on_selection_change=lambda e: setattr(form_state, 'priority', e.selection),
                style=me.Style(margin=me.Margin(bottom=10)),
            )
            
            with me.content_button(
                type='raised',
                on_click=submit_ticket,
                disabled=app_state.loading,
            ):
                me.text('Submit Ticket' if not app_state.loading else 'Processing...')
        
        # Messages
        if app_state.messages:
            me.text('Responses', style=me.Style(font_size=18, font_weight='bold', margin=me.Margin(bottom=10)))
            for msg in reversed(app_state.messages):
                with me.box(style=me.Style(
                    border=me.Border.all(me.BorderSide(width=1, color='#ddd', style='solid')),
                    padding=me.Padding.all(15),
                    margin=me.Margin(bottom=10),
                    border_radius=8,
                    background='#f5f5f5' if msg['role'] == 'user' else '#e3f2fd',
                )):
                    me.text(
                        f"{'You' if msg['role'] == 'user' else 'Agent'}:",
                        style=me.Style(font_weight='bold', margin=me.Margin(bottom=5)),
                    )
                    me.text(msg['content'], style=me.Style(white_space='pre-wrap'))


if __name__ == '__main__':
    me.run(port=12000)
