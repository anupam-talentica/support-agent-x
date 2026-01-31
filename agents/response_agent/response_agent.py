"""Response Synthesis Agent - Generates human-readable support responses."""

import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def create_response_agent() -> LlmAgent:
    """Constructs the ADK response synthesis agent."""
    LITELLM_MODEL = "openai/gpt-4.1-mini"
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='response_agent',
        description='An agent that synthesizes human-readable support responses',
        instruction="""You are a response synthesis agent. Your primary function is to take processed ticket information and generate a helpful, professional support response.

When generating a response, structure it in Markdown format with the following sections:

1. **Summary**: A brief one-sentence summary of the issue
2. **Details**: Detailed explanation of what was identified
3. **Next Steps**: Actionable steps the user or support team should take
4. **Additional Information**: Any relevant context or notes

Be professional, clear, and helpful. If the ticket information is incomplete, acknowledge that and suggest what additional information might be needed.

Format your response in clean Markdown with proper headings and bullet points.""",
        tools=[],  # No tools needed - just LLM processing
    )
