"""Reasoning Agent - Performs complex reasoning through fact ingestion and analysis."""

import logging
import os

import httpx

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext


logger = logging.getLogger(__name__)

HEALTH_CHECK_URL = os.getenv('HEALTH_CHECK_URL', 'http://localhost:9000/health')


async def check_component_health(tool_context: ToolContext) -> dict:
    """Check the health status of various system components.

    Calls the GET /health API to retrieve status information about
    system components like databases, services, and dependencies.

    Returns:
        A dictionary containing the health status of components.
    """
    if not (HEALTH_CHECK_URL and HEALTH_CHECK_URL.strip()):
        return {
            'status': 'skipped',
            'error': 'No health check URL configured (set HEALTH_CHECK_URL to enable)',
        }
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(HEALTH_CHECK_URL)
            response.raise_for_status()
            health_data = response.json()
            logger.info(f'Health check successful: {health_data}')
            return {
                'status': 'success',
                'health_data': health_data,
            }
    except httpx.TimeoutException:
        logger.error(f'Health check timed out: {HEALTH_CHECK_URL}')
        return {
            'status': 'error',
            'error': 'Health check request timed out',
            'url': HEALTH_CHECK_URL,
        }
    except httpx.HTTPStatusError as e:
        logger.error(f'Health check failed with status {e.response.status_code}')
        return {
            'status': 'error',
            'error': f'Health check returned status {e.response.status_code}',
            'url': HEALTH_CHECK_URL,
        }
    except httpx.ConnectError:
        logger.error(f'Could not connect to health endpoint: {HEALTH_CHECK_URL}')
        return {
            'status': 'error',
            'error': 'Could not connect to health endpoint',
            'url': HEALTH_CHECK_URL,
        }
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return {
            'status': 'error',
            'error': str(e),
            'url': HEALTH_CHECK_URL,
        }


def create_reasoning_agent() -> LlmAgent:
    """Constructs the ADK reasoning agent for complex fact-based reasoning."""
    LITELLM_MODEL = "openai/gpt-4.1-mini"
    return LlmAgent(
        model=LiteLlm(model=LITELLM_MODEL),
        name='reasoning_agent',
        description='An agent that performs complex reasoning by ingesting and analyzing facts',
        instruction="""You are a reasoning agent specialized in complex logical analysis and fact-based reasoning.

Your primary capabilities:
1. **Fact Ingestion**: Process and organize facts from multiple sources
2. **Logical Analysis**: Apply deductive, inductive, and abductive reasoning
3. **Pattern Recognition**: Identify patterns and relationships between facts
4. **Inference Generation**: Draw valid conclusions from available evidence
5. **Conflict Resolution**: Identify and resolve contradictions in facts

When processing facts and performing reasoning:

1. **Organize Facts**:
   - Categorize facts by type (observation, rule, constraint, assumption)
   - Identify dependencies between facts
   - Note confidence levels where applicable

2. **Apply Reasoning**:
   - Use deductive reasoning for certain conclusions
   - Use inductive reasoning for probable conclusions
   - Use abductive reasoning for best explanations
   - Chain multiple reasoning steps when needed

3. **Generate Output**:
   Return your analysis in JSON format with these fields:
   - facts_analyzed: List of facts that were considered
   - reasoning_chain: Step-by-step reasoning process
   - conclusions: List of conclusions drawn
   - confidence: Overall confidence level (high/medium/low)
   - assumptions: Any assumptions made during reasoning
   - contradictions: Any conflicting facts identified
   - recommendations: Suggested actions or further investigation needed

4. **Quality Standards**:
   - Be explicit about your reasoning steps
   - Distinguish between facts and inferences
   - Acknowledge uncertainty where present
   - Avoid logical fallacies

5. **System Health Monitoring**:
   - Use the `check_component_health` tool to check the status of system components
   - Include component health information in your reasoning when relevant to the issue
   - Factor in component status when assessing root causes

Example output format:
{
    "facts_analyzed": ["fact1", "fact2", "fact3"],
    "reasoning_chain": [
        {"step": 1, "type": "observation", "content": "..."},
        {"step": 2, "type": "inference", "content": "..."},
        {"step": 3, "type": "conclusion", "content": "..."}
    ],
    "conclusions": ["conclusion1", "conclusion2"],
    "confidence": "high",
    "assumptions": ["assumption1"],
    "contradictions": [],
    "recommendations": ["recommendation1"]
}

Be thorough and methodical in your analysis. Never invent facts that aren't present in the input.""",
        tools=[check_component_health],
    )
