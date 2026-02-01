"""Input guardrail for user messages.

Validates and optionally sanitizes text before it is sent to agents.
Covers length limits, prompt-injection patterns, basic sanitization,
and optional LLM-based classification.

**Allowed scope (enforced by LLM when use_llm=True): Ecommerce domain**
- Anything related to ecommerce is allowed: Billing (payments, refunds, returns, invoices), Account, Orders, Products, Shipping, Coupons, Support tickets for ecommerce issues.
- Rejected only: non-ecommerce topics (e.g. travel booking), prompt injection, harmful content.
"""

import re
from dataclasses import dataclass
from typing import Sequence

# Default limits (configurable via env or caller)
DEFAULT_MAX_LENGTH = 32_000
DEFAULT_MIN_LENGTH = 1

# Patterns often associated with prompt injection / jailbreak attempts (case-insensitive)
PROMPT_INJECTION_PATTERNS: tuple[str, ...] = (
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|above|prior)",
    r"forget\s+(everything|all)\s+(you\s+)?(were\s+)?(told|trained)",
    r"you\s+are\s+now\s+in\s+(?:a\s+)?(?:new\s+)?(?:role|mode|character)",
    r"system\s*:\s*you\s+are",
    r"\[system\]\s*:",
    r"<\|?system\|?>",
    r"\[INST\]\s*.*\s*\[\/INST\]",  # instruction-style override
    r"override\s+(your\s+)?(instructions|rules|guidelines)",
    r"pretend\s+you\s+(?:are|have)\s+no\s+(?:restrictions|limits|guidelines)",
    r"jailbreak",
    r"developer\s+mode",
    r"dan\s+mode",
    r"\/\/\s*ignore\s+previous",  # comment-style
)

# Precompiled regexes for performance
_PROMPT_INJECTION_RE = re.compile(
    "|".join(f"(?:{p})" for p in PROMPT_INJECTION_PATTERNS),
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class GuardrailResult:
    """Result of input guardrail validation."""

    success: bool
    """True if input passed all checks."""
    sanitized_text: str | None
    """Sanitized text to use when success is True; None when failed or no changes."""
    error_code: str | None
    """Short code for programmatic handling: empty, too_long, prompt_injection, invalid."""
    message: str
    """Human-readable message for API responses or logs."""


def validate_input(
    text: str,
    *,
    max_length: int = DEFAULT_MAX_LENGTH,
    min_length: int = DEFAULT_MIN_LENGTH,
    check_prompt_injection: bool = True,
    sanitize: bool = True,
    custom_blocklist: Sequence[str] | None = None,
) -> GuardrailResult:
    """Run input guardrail on user text.

    Args:
        text: Raw user input.
        max_length: Maximum allowed character length.
        min_length: Minimum allowed character length (after sanitization).
        check_prompt_injection: Whether to check for common prompt-injection patterns.
        sanitize: Whether to sanitize (strip null bytes, normalize whitespace).
        custom_blocklist: Optional list of exact substrings to reject (case-insensitive).

    Returns:
        GuardrailResult with success, optional sanitized_text, error_code, and message.
    """
    if not isinstance(text, str):
        return GuardrailResult(
            success=False,
            sanitized_text=None,
            error_code="invalid",
            message="Your request could not be processed because the input format is invalid. Please send a text message.",
        )

    working = text

    if sanitize:
        # Remove null bytes and other control characters
        working = "".join(c for c in working if ord(c) >= 32 or c in "\n\r\t")
        # Collapse multiple spaces/newlines to at most 2 newlines, trim
        working = re.sub(r"[ \t]+", " ", working)
        working = re.sub(r"\n{3,}", "\n\n", working)
        working = working.strip()

    if len(working) < min_length:
        return GuardrailResult(
            success=False,
            sanitized_text=None,
            error_code="empty",
            message="Your request could not be processed because the message is empty. Please type your question or describe your issue (e.g. billing, account, or support ticket) and try again.",
        )

    if len(working) > max_length:
        return GuardrailResult(
            success=False,
            sanitized_text=None,
            error_code="too_long",
            message=f"Your request could not be processed because the message is too long (maximum {max_length:,} characters). Please shorten your message and try again.",
        )

    if check_prompt_injection and _PROMPT_INJECTION_RE.search(working):
        return GuardrailResult(
            success=False,
            sanitized_text=None,
            error_code="prompt_injection",
            message="Your request could not be processed because it contains instructions that this chat is not designed to follow. Please ask only about billing, your account, or support tickets (e.g. payments, refunds, login, or ticket status) and we’ll be happy to help.",
        )

    if custom_blocklist:
        lower_working = working.lower()
        for phrase in custom_blocklist:
            if phrase and phrase.lower() in lower_working:
                return GuardrailResult(
                    success=False,
                    sanitized_text=None,
                    error_code="blocked",
                    message="Your request could not be processed because it contains content that is not permitted. Please rephrase your message and ask about billing, account, or support tickets only.",
                )

    return GuardrailResult(
        success=True,
        sanitized_text=working if (sanitize and working != text) else None,
        error_code=None,
        message="OK",
    )


async def validate_input_with_llm(
    text: str,
    *,
    max_length: int = DEFAULT_MAX_LENGTH,
    min_length: int = DEFAULT_MIN_LENGTH,
    check_prompt_injection: bool = True,
    sanitize: bool = True,
    custom_blocklist: Sequence[str] | None = None,
    use_llm: bool = True,
) -> GuardrailResult:
    """Run rule-based guardrail then LLM classification. Use this for proper input guardrailing.

    Same rules as validate_input(); if all pass and use_llm is True, calls the LLM
    to classify the message (prompt injection, off-topic, harmful, etc.). Async so
    it can be awaited from API handlers.

    This is the single input guardrail. It is invoked at the Host (first agent) for
    both REST (/api/chat, /api/chat/stream) and A2A so off-topic/rejected messages
    never reach Ingestion or Planner. For faster rejection latency, use a smaller
    model or lower GUARDRAIL_LLM_TIMEOUT in llm_guardrail.

    Args:
        text: Raw user input.
        max_length: Maximum allowed character length.
        min_length: Minimum allowed character length (after sanitization).
        check_prompt_injection: Whether to apply regex prompt-injection check (fast pre-filter).
        sanitize: Whether to sanitize (strip null bytes, normalize whitespace).
        custom_blocklist: Optional list of exact substrings to reject (case-insensitive).
        use_llm: Whether to run LLM classification after rule-based checks.

    Returns:
        GuardrailResult; success=False with error_code/reason when rules or LLM reject.
    """
    # Rule-based checks first (sync)
    result = validate_input(
        text,
        max_length=max_length,
        min_length=min_length,
        check_prompt_injection=check_prompt_injection,
        sanitize=sanitize,
        custom_blocklist=custom_blocklist,
    )
    if not result.success:
        return result

    if not use_llm:
        return result

    from agents.guardrails_agent.llm_guardrail import check_input_llm

    working = result.sanitized_text or text
    llm_result = await check_input_llm(working)
    if llm_result.allowed:
        return result
    # Use LLM reason when present; otherwise give a clear reason by category
    user_message = llm_result.reason
    if not user_message or not user_message.strip():
        user_message = _user_facing_reason_for_category(llm_result.category)
    return GuardrailResult(
        success=False,
        sanitized_text=None,
        error_code=llm_result.category,
        message=user_message,
    )


def _user_facing_reason_for_category(category: str) -> str:
    """Return a user-friendly reason why the request could not be processed."""
    reasons = {
        "off_topic": "Your request could not be processed because this chat supports Ecommerce-related questions only (orders, products, returns, refunds, billing, account, support). We don’t handle flight or train booking, travel, or other non-ecommerce topics. Please ask about your orders, account, or support.",
        "prompt_injection": "Your request could not be processed because it contains instructions this chat is not designed to follow. Please ask only about your orders, account, or ecommerce support and we’ll be happy to help.",
        "harmful": "Your request could not be processed because it appears to contain content that we cannot assist with. Please rephrase and limit your question to ecommerce (orders, products, returns, billing, account, or support).",
        "other": "Your request could not be processed. This chat supports Ecommerce-related questions only (orders, products, returns, refunds, billing, account, support). Please rephrase your message accordingly.",
    }
    return reasons.get(category, reasons["other"])
