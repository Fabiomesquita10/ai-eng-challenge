"""Output checks: redact sensitive data, validate response safety."""

import re
from typing import Optional, Tuple

# IBAN: 2 letters + 2 digits + spaces/digits (e.g. PT50 0000 0000 0000 0000 0000 0)
IBAN_PATTERN = re.compile(
    r"\b([A-Z]{2}\d{2}[\s\d]{15,35})\b",
    re.IGNORECASE,
)
# Card-like: 4 groups of 4 digits (with optional space/dash)
CARD_PATTERN = re.compile(r"\b(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b")
# Full card: 13-19 consecutive digits
FULL_CARD_PATTERN = re.compile(r"\b\d{13,19}\b")


def _get_llm():
    """Lazy import."""
    from langchain_openai import ChatOpenAI
    from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
    if not OPENAI_API_KEY:
        return None
    return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.0)


def redact_sensitive(text: str) -> str:
    """
    Redact IBAN, card numbers, and similar from response.
    """
    if not text:
        return text
    result = text
    # IBAN - mask middle
    result = IBAN_PATTERN.sub(lambda m: _mask_iban(m.group(1)), result)
    # Card with separators
    result = CARD_PATTERN.sub(lambda m: _mask_card(m.group(1)), result)
    # Long digit sequences
    result = FULL_CARD_PATTERN.sub("****-****-****-****", result)
    return result


def _mask_iban(iban: str) -> str:
    cleaned = re.sub(r"[\s-]", "", iban)
    if len(cleaned) >= 8:
        return cleaned[:4] + "*" * (len(cleaned) - 8) + cleaned[-4:]
    return "****"


def _mask_card(card: str) -> str:
    digits = re.sub(r"[\s-]", "", card)
    if len(digits) >= 4:
        return "****-****-****-" + digits[-4:]
    return "****"


def check_output_llm(response: str, user_message: str) -> Tuple[bool, Optional[str]]:
    """
    LLM-based output check. Returns (flagged, reason).
    Flags: reveals full sensitive data, promises actions not performed, invents approvals, unprofessional tone.
    """
    llm = _get_llm()
    if not llm:
        return False, None

    prompt = """You are a banking compliance checker. Classify if this AI response is UNSAFE or SAFE.

UNSAFE = the response:
- Reveals full IBAN, card numbers, or other sensitive identifiers
- Promises actions the system does not perform (e.g. "I've approved your loan", "Your card is now unblocked")
- Invents approvals, transfers, or confirmations
- Uses unprofessional, offensive, or inappropriate tone

SAFE = professional, accurate, does not promise unauthorized actions.

User asked: "{user_msg}"
AI response: "{response}"

Respond with exactly one line: UNSAFE: <short reason> or SAFE""".format(
        user_msg=user_message.replace('"', "'")[:200],
        response=response.replace('"', "'")[:800],
    )

    try:
        resp = llm.invoke(prompt)
        content = (resp.content if hasattr(resp, "content") else str(resp)).strip().upper()
        if content.startswith("UNSAFE"):
            reason = content.replace("UNSAFE:", "").strip() or "LLM classified as unsafe"
            return True, reason
    except Exception:
        pass
    return False, None


def check_output(response: str, user_message: str) -> Tuple[str, bool, Optional[str]]:
    """
    Full output check: redact first, then LLM.
    Returns (redacted_response, flagged, reason).
    """
    redacted = redact_sensitive(response)
    flagged, reason = check_output_llm(redacted, user_message)
    return redacted, flagged, reason
