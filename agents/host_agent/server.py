"""REST API Server for Host Agent.

This module provides REST API endpoints for the Host Agent,
allowing external applications (like React UIs) to interact
with the multi-agent support system.
"""

import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.genai import types


logger = logging.getLogger(__name__)


# --- Pydantic Models for REST API ---

class ChatMessage(BaseModel):
    """A single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str


class SendMessageRequest(BaseModel):
    """Request body for sending a message to the host agent."""
    message: str
    conversation_id: str | None = None
    conversation_history: list[ChatMessage] | None = None


class SendMessageResponse(BaseModel):
    """Response from the host agent after processing a message."""
    success: bool
    message_id: str
    conversation_id: str
    response: str
    status: str  # "completed", "failed", "working"
    agents_used: list[str] = []  # Which agents were involved in processing


class AgentInfo(BaseModel):
    """Information about a connected remote agent."""
    name: str
    description: str | None
    url: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agents_connected: int
    agents: list[str] = []


class RegisterAgentRequest(BaseModel):
    """Request body for registering a new remote agent."""
    url: str


class RegisterAgentResponse(BaseModel):
    """Response after registering a remote agent."""
    success: bool
    agent_name: str | None = None
    url: str
    error: str | None = None


# --- Global State (set by main module) ---
host_agent_instance = None
runner_instance = None
session_service = None


def set_dependencies(host_agent, runner, session_svc):
    """Set the dependencies for the API endpoints.
    
    This should be called from the main module after initializing
    the host agent and runner.
    """
    global host_agent_instance, runner_instance, session_service
    host_agent_instance = host_agent
    runner_instance = runner
    session_service = session_svc


def create_api_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Host Agent API",
        description="REST API for the Support Agent Host - routes tickets through support agents",
        version="1.0.0",
    )

    # Add CORS middleware for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "*",  # Allow all origins in development - restrict in production
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Endpoint Definitions ---

    @app.get("/agents", response_model=list[AgentInfo])
    async def list_agents():
        """List all connected remote agents."""
        if not host_agent_instance:
            raise HTTPException(status_code=503, detail="Host agent not initialized")
        
        return [
            AgentInfo(
                name=card.name,
                description=card.description,
                url=card.url,
            )
            for card in host_agent_instance.cards.values()
        ]

    @app.post("/chat", response_model=SendMessageResponse)
    async def send_message(request: SendMessageRequest):
        """
        Send a message to the host agent and get a response.
        
        The host agent will route the message through the appropriate support agents
        (Ingestion Agent → Response Agent) and return the final response.
        """
        if not host_agent_instance or not runner_instance or not session_service:
            raise HTTPException(status_code=503, detail="Host agent not initialized")
        
        # Generate IDs
        message_id = str(uuid.uuid4())
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or create session
        session = await session_service.get_session(
            app_name='Host Agent',
            user_id='api_user',
            session_id=conversation_id,
        )
        if session is None:
            session = await session_service.create_session(
                app_name='Host Agent',
                user_id='api_user',
                session_id=conversation_id,
            )
        
        # Create the message content
        content = types.Content(
            parts=[types.Part.from_text(text=request.message)],
            role='user'
        )
        
        # Track which agents were used
        agents_used = []
        response_parts = []
        status = "completed"
        
        try:
            async for event in runner_instance.run_async(
                user_id='api_user',
                session_id=conversation_id,
                new_message=content,
            ):
                # Track function calls (agent delegations)
                if event.get_function_calls():
                    for fc in event.get_function_calls():
                        if fc.name == 'send_message' and fc.args:
                            agent_name = fc.args.get('agent_name')
                            if agent_name and agent_name not in agents_used:
                                agents_used.append(agent_name)
                
                # Extract text from event content
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
                
                # Check if this is the final response
                if event.is_final_response():
                    break
                    
        except Exception as e:
            logger.error(f'Error processing message: {e}')
            return SendMessageResponse(
                success=False,
                message_id=message_id,
                conversation_id=conversation_id,
                response=f"Error processing request: {str(e)}",
                status="failed",
                agents_used=agents_used,
            )
        
        # Combine all response parts
        response_text = '\n'.join(response_parts) if response_parts else 'No response generated'
        
        return SendMessageResponse(
            success=True,
            message_id=message_id,
            conversation_id=conversation_id,
            response=response_text,
            status=status,
            agents_used=agents_used,
        )

    @app.get("/chat/stream")
    async def send_message_stream(message: str, conversation_id: str | None = None):
        """
        Send a message and stream the response using Server-Sent Events (SSE).
        
        Events emitted:
        - `status`: Progress updates (e.g., "Delegating to Ingestion Agent")
        - `agent`: When a specific agent is being called
        - `message`: The final response (JSON with response, conversation_id, agents_used)
        - `error`: If an error occurs
        - `done`: Stream complete
        """
        if not host_agent_instance or not runner_instance or not session_service:
            raise HTTPException(status_code=503, detail="Host agent not initialized")
        
        conv_id = conversation_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        async def event_generator() -> AsyncGenerator[str, None]:
            # Get or create session
            session = await session_service.get_session(
                app_name='Host Agent',
                user_id='api_user',
                session_id=conv_id,
            )
            if session is None:
                session = await session_service.create_session(
                    app_name='Host Agent',
                    user_id='api_user',
                    session_id=conv_id,
                )
            
            # Create the message content
            content = types.Content(
                parts=[types.Part.from_text(text=message)],
                role='user'
            )
            
            # Track agents used
            agents_used = []
            
            # Send initial status
            yield f"event: status\ndata: {json.dumps({'status': 'processing', 'message': 'Processing your request...'})}\n\n"
            
            try:
                async for event in runner_instance.run_async(
                    user_id='api_user',
                    session_id=conv_id,
                    new_message=content,
                ):
                    # Send status updates for non-final events
                    if not event.is_final_response():
                        if event.get_function_calls():
                            # Agent is calling a tool/function
                            for fc in event.get_function_calls():
                                if fc.name == 'send_message' and fc.args:
                                    agent_name = fc.args.get('agent_name', 'unknown')
                                    if agent_name not in agents_used:
                                        agents_used.append(agent_name)
                                    yield f"event: agent\ndata: {json.dumps({'agent': agent_name, 'status': 'delegating'})}\n\n"
                        elif event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    yield f"event: status\ndata: {json.dumps({'status': 'working', 'message': part.text[:200]})}\n\n"
                    else:
                        # Final response - send the message event
                        response_text = ''
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    response_text += part.text + '\n'
                        
                        final_response = {
                            'success': True,
                            'message_id': message_id,
                            'conversation_id': conv_id,
                            'response': response_text.strip(),
                            'status': 'completed',
                            'agents_used': agents_used,
                        }
                        yield f"event: message\ndata: {json.dumps(final_response)}\n\n"
                        break
            except Exception as e:
                logger.error(f'Error in stream: {e}')
                error_response = {
                    'success': False,
                    'message_id': message_id,
                    'conversation_id': conv_id,
                    'error': str(e),
                    'status': 'failed',
                    'agents_used': agents_used,
                }
                yield f"event: error\ndata: {json.dumps(error_response)}\n\n"
            
            yield f"event: done\ndata: {json.dumps({'conversation_id': conv_id})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    @app.post("/agents/register", response_model=RegisterAgentResponse)
    async def register_agent(request: RegisterAgentRequest):
        """Register a new remote agent by URL."""
        if not host_agent_instance:
            raise HTTPException(status_code=503, detail="Host agent not initialized")
        
        try:
            import httpx
            from a2a.client import A2ACardResolver
            from .remote_agent_connection import RemoteAgentConnections
            
            async with httpx.AsyncClient(timeout=30) as client:
                card_resolver = A2ACardResolver(client, request.url)
                card = await card_resolver.get_agent_card()
                
                remote_connection = RemoteAgentConnections(
                    agent_card=card, agent_url=request.url
                )
                host_agent_instance.remote_agent_connections[card.name] = remote_connection
                host_agent_instance.cards[card.name] = card
                
                # Update agents string for LLM context
                agent_info = []
                for agent_detail_dict in host_agent_instance.list_remote_agents():
                    agent_info.append(json.dumps(agent_detail_dict))
                host_agent_instance.agents = '\n'.join(agent_info)
            
            return RegisterAgentResponse(
                success=True,
                agent_name=card.name,
                url=request.url,
            )
        except Exception as e:
            logger.error(f'Failed to register agent: {e}')
            return RegisterAgentResponse(
                success=False,
                url=request.url,
                error=str(e),
            )

    return app


# Create the API app instance
api_app = create_api_app()
