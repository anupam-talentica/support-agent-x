"""Output guardrail for agent responses.

Prevents exposing company-sensitive data, company finances, and other
information that should not be shared with users. Redacts or replaces
sensitive content before responses are sent to the user.
"""

import json
import logging
import os
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Placeholder for redacted content
REDACTED_PLACEHOLDER = "[REDACTED]"

# Generic message when response is blocked entirely due to sensitivity
BLOCKED_MESSAGE = "I'm not able to share that information. For details about your account or billing, please contact support."

# Dollar amounts: $1, $1.00, $1,000, $1,000,000.00 (redact to avoid exposing company/customer figures)
_PATTERN_CURRENCY = re.compile(
    r"\$\s*[\d,]+(?:\.[\d]{2})?\s*(?:USD|dollars?)?|"
    r"(?:USD|EUR|GBP)\s*[\d,]+(?:\.[\d]{2})?",
    re.IGNORECASE,
)

# SSN-style (XXX-XX-XXXX)
_PATTERN_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

# Credit card style (4 groups of 4 digits, optional spaces/dashes)
_PATTERN_CARD = re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b")

# Bank account / internal ID style (long numeric strings that might be internal refs)
_PATTERN_LONG_NUMERIC = re.compile(r"\b\d{10,}\b")

# Phrases that indicate company-internal or confidential content (redact surrounding or block)
_SENSITIVE_PHRASES = re.compile(
    r"(?:"
    r"internal\s+only|confidential|proprietary|do\s+not\s+share|"
    r"company\s+revenue|company\s+finances|our\s+revenue|our\s+profit|"
    r"EBITDA|earnings\s+before|net\s+income\s+was|revenue\s+was|"
    r"salary|compensation\s+package|employee\s+pay|"
    r"budget\s+allocation|internal\s+budget|"
    r"margin\s+is\s+\d|growth\s+rate\s+of\s+\d|"
    r"Q[1-4]\s+results|quarterly\s+earnings|"
    r"board\s+meeting|executive\s+session|"
    r"trade\s+secret|NDA|non-?disclosure"
    r")",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OutputGuardrailResult:
    """Result of output guardrail processing."""

    safe: bool
    """True if the response is safe to send (after any redactions)."""
    redacted_text: str
    """Text to send to the user (redacted or original)."""
    was_modified: bool
    """True if redaction or replacement was applied."""
    blocked: bool
    """True if the response was replaced entirely with a generic message."""


def apply_output_guardrail(
    text: str,
    *,
    redact_currency: bool = True,
    redact_ssn_card: bool = True,
    redact_long_numeric: bool = True,
    redact_sensitive_phrases: bool = True,
    block_on_sensitive_phrases: bool = False,
) -> OutputGuardrailResult:
    """Apply rule-based output guardrail to response text.

    Redacts or blocks company-sensitive data, finances, and other
    information that should not be shared with users.

    Args:
        text: Raw response text from the agent.
        redact_currency: Redact currency amounts (e.g. $1,000, USD 500).
        redact_ssn_card: Redact SSN and credit-card-style numbers.
        redact_long_numeric: Redact long numeric strings (e.g. internal IDs).
        redact_sensitive_phrases: Redact sentences/phrases containing sensitive keywords.
        block_on_sensitive_phrases: If True, replace entire response with BLOCKED_MESSAGE
            when sensitive phrases are found; otherwise only redact the phrase.

    Returns:
        OutputGuardrailResult with safe, redacted_text, was_modified, blocked.
    """
    if not text or not isinstance(text, str):
        return OutputGuardrailResult(
            safe=True,
            redacted_text=text or "",
            was_modified=False,
            blocked=False,
        )

    working = text
    modified = False

    if redact_currency:
        working, n = _PATTERN_CURRENCY.subn(REDACTED_PLACEHOLDER, working)
        if n:
            modified = True

    if redact_ssn_card:
        working, n = _PATTERN_SSN.subn(REDACTED_PLACEHOLDER, working)
        if n:
            modified = True
        working, n = _PATTERN_CARD.subn(REDACTED_PLACEHOLDER, working)
        if n:
            modified = True

    if redact_long_numeric:
        working, n = _PATTERN_LONG_NUMERIC.subn(REDACTED_PLACEHOLDER, working)
        if n:
            modified = True

    if redact_sensitive_phrases or block_on_sensitive_phrases:
        if _SENSITIVE_PHRASES.search(working):
            if block_on_sensitive_phrases:
                return OutputGuardrailResult(
                    safe=True,
                    redacted_text=BLOCKED_MESSAGE,
                    was_modified=True,
                    blocked=True,
                )
            # Redact the sensitive phrase (replace match with placeholder)
            working = _SENSITIVE_PHRASES.sub(REDACTED_PLACEHOLDER, working)
            modified = True

    return OutputGuardrailResult(
        safe=True,
        redacted_text=working.strip() if working else "",
        was_modified=modified,
        blocked=False,
    )


# --- Optional LLM-based output check ---
_OUTPUT_GUARDRAIL_MODEL = os.getenv("LITELLM_MODEL", "openai/gpt-4.1-mini")
_OUTPUT_GUARDRAIL_TIMEOUT = float(os.getenv("GUARDRAIL_LLM_TIMEOUT", "10.0"))

_OUTPUT_SYSTEM_PROMPT = """You are an output guardrail for a customer support chat. Your job is to decide if a response (that the system is about to send to the user) contains information that must NOT be shared with users.

**BLOCK (contains_sensitive: true)** when the response contains ANY of:
- Company finances: revenue, profit, EBITDA, margins, quarterly earnings, growth rates, budget figures, financial projections
- Internal/confidential: "internal only", "confidential", "proprietary", "do not share", trade secrets, NDA content
- Employee/HR: salaries, compensation, employee pay, performance ratings
- Unreleased product/strategy: roadmap details, pricing strategy, M&A, unreleased features
- Any specific numbers or data that look like company-internal metrics or PII that shouldn't be in a user-facing response

**ALLOW (contains_sensitive: false)** when the response is generic support help, account/billing guidance (without exposing internal figures), ticket status, or safe how-to content.

Respond with valid JSON only: {"contains_sensitive": true or false, "reason": "one short phrase"}"""


async def apply_output_guardrail_with_llm(
    text: str,
    *,
    use_llm: bool = True,
    **rule_kwargs,
) -> OutputGuardrailResult:
    """Apply rule-based guardrail, then optionally LLM check. Use for full protection.

    Rule-based redaction runs first; if use_llm is True, the (redacted) text
    is checked by an LLM. If the LLM says it contains sensitive content, the
    entire response is replaced with BLOCKED_MESSAGE.
    """
    result = apply_output_guardrail(text, **rule_kwargs)
    if not use_llm or not result.redacted_text:
        return result
    try:
        from litellm import acompletion
    except ImportError:
        return result
    snippet = result.redacted_text[:6000]
    if len(result.redacted_text) > 6000:
        snippet += "\n\n[Truncated for check.]"
    try:
        response = await acompletion(
            model=_OUTPUT_GUARDRAIL_MODEL,
            messages=[
                {"role": "system", "content": _OUTPUT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Does this response contain sensitive data that must not be shared with the user?\n\n{snippet}"},
            ],
            timeout=_OUTPUT_GUARDRAIL_TIMEOUT,
            max_tokens=128,
        )
    except Exception as e:
        logger.warning("Output guardrail LLM call failed: %s", e)
        return result
    content = None
    if response and response.choices:
        content = response.choices[0].message.content
    if not content:
        return result
    content = (content or "").strip()
    if "```" in content:
        start = content.find("```")
        if start != -1:
            start = content.find("\n", start) + 1 if "\n" in content[start:] else start + 3
            end = content.find("```", start)
            if end != -1:
                content = content[start:end]
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return result
    if not isinstance(data, dict):
        return result
    contains_sensitive = data.get("contains_sensitive")
    if not isinstance(contains_sensitive, bool) or not contains_sensitive:
        return result
    return OutputGuardrailResult(
        safe=True,
        redacted_text=BLOCKED_MESSAGE,
        was_modified=True,
        blocked=True,
    )
