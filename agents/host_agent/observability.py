"""Langfuse observability for Host Agent.

Tracks request progression through the orchestrator:
- One trace per user request (REST or A2A)
- Spans for each step: Host Agent processing, delegation to Ingestion/Planner agents

Requires env: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY (optional: LANGFUSE_BASE_URL).
If not set, all helpers no-op so the app runs without Langfuse.
See: https://langfuse.com/docs/sdk/python
"""

import contextlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_langfuse_client = None


def _get_langfuse():
    """Lazy-init Langfuse client. Returns None if credentials not set."""
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client
    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    sk = os.getenv("LANGFUSE_SECRET_KEY")
    if not pk or not sk:
        logger.info(
            "Langfuse observability disabled (LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set)."
        )
        return None
    try:
        from langfuse import get_client

        _langfuse_client = get_client()
        if _langfuse_client.auth_check():
            logger.info("Langfuse observability enabled.")
        else:
            logger.warning("Langfuse auth check failed. Observability disabled.")
            _langfuse_client = None
    except Exception as e:
        logger.warning("Langfuse init failed: %s. Observability disabled.", e)
        _langfuse_client = None
    return _langfuse_client


def is_enabled() -> bool:
    """Return True if Langfuse is configured and usable."""
    return _get_langfuse() is not None


def log_status() -> bool:
    """Initialize Langfuse (if configured) and log status at startup. Returns True if enabled."""
    return _get_langfuse() is not None


@contextlib.contextmanager
def trace_request(
    name: str = "host-agent-request",
    *,
    session_id: str | None = None,
    user_id: str | None = None,
    input_data: Any = None,
    metadata: dict[str, Any] | None = None,
):
    """Context manager: one trace per request. Use at REST/A2A entry points."""
    langfuse = _get_langfuse()
    if not langfuse:
        yield None
        return

    try:
        with langfuse.start_as_current_observation(
            as_type="span",
            name=name,
            input=input_data,
            metadata=metadata or {},
        ) as span:
            if session_id or user_id:
                from langfuse import propagate_attributes

                with propagate_attributes(
                    session_id=(session_id or ""),
                    user_id=(user_id or ""),
                ):
                    yield span
            else:
                yield span
    except Exception as e:
        logger.debug("Langfuse trace_request error: %s", e)
        yield None


@contextlib.contextmanager
def span_agent_call(agent_name: str, task_input: str | None = None):
    """Context manager: one span per delegation to a remote agent (Ingestion, Planner, etc.)."""
    langfuse = _get_langfuse()
    if not langfuse:
        yield None
        return

    try:
        with langfuse.start_as_current_observation(
            as_type="span",
            name=f"delegate-to-{agent_name}",
            input={"agent": agent_name, "task": (task_input or "")[:2000]},
            metadata={"agent_name": agent_name},
        ) as span:
            yield span
    except Exception as e:
        logger.debug("Langfuse span_agent_call error: %s", e)
        yield None


def update_current_span(output: Any = None, metadata: dict[str, Any] | None = None) -> None:
    """Update the currently active observation (e.g. set output when request completes)."""
    langfuse = _get_langfuse()
    if not langfuse:
        return
    try:
        langfuse.update_current_span(output=output, metadata=metadata or {})
    except Exception as e:
        logger.debug("Langfuse update_current_span error: %s", e)


def flush() -> None:
    """Flush buffered events to Langfuse. Call in short-lived handlers if needed."""
    langfuse = _get_langfuse()
    if langfuse:
        try:
            langfuse.flush()
        except Exception as e:
            logger.debug("Langfuse flush error: %s", e)
