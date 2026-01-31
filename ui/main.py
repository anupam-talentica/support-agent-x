"""Simplified UI for Support Agents Demo."""

import os
import uuid

import httpx
import mesop as me

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, Part, Role, SendMessageRequest, TextPart
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
        # Get agent card
        async with httpx.AsyncClient(timeout=30) as client:
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
            
            # Get task updates
            if hasattr(response.root, 'result') and hasattr(response.root.result, 'id'):
                task_id = response.root.result.id
                async for update in a2a_client.get_task_updates(task_id):
                    if update.root.type == 'task_artifact_update':
                        if hasattr(update.root, 'artifact') and update.root.artifact:
                            if hasattr(update.root.artifact, 'parts'):
                                for part in update.root.artifact.parts:
                                    if part.type == 'text':
                                        state.messages.append({
                                            'role': 'assistant',
                                            'content': part.text,
                                        })
                                        yield
                    elif update.root.type == 'task_status_update':
                        if hasattr(update.root, 'status') and update.root.status == 'completed':
                            break
            
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
