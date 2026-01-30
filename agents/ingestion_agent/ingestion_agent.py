"""Ingestion Agent - Normalizes and extracts ticket information."""

import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def create_ingestion_agent() -> LlmAgent:
    """Constructs the ADK ingestion agent."""
    LITELLM_MODEL = os.getenv('LITELLM_MODEL', 'gemini-2.5-flash')
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='ingestion_agent',
        description='An agent that normalizes and extracts ticket information',
        instruction="""You are a ticket ingestion agent. Your primary function is to normalize user input and extract structured information from support tickets.

When processing a ticket, extract and return the following information in JSON format:
- title: A clear, concise title summarizing the issue
- description: The full description of the problem
- priority: One of P0 (critical), P1 (high), P2 (medium), P3 (low), P4 (lowest). Default to P3 if not specified.
- error_codes: Any error codes mentioned (as a list)
- affected_systems: Systems or services mentioned (as a list)
- urgency_indicators: Keywords indicating urgency (e.g., "down", "failing", "broken")

Return your response as a JSON object with these fields. Be thorough in extraction but don't invent information that isn't present in the input.""",
        tools=[],  # No tools needed - just LLM processing
    )
