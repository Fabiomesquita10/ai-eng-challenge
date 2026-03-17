"""Safe rewrite: rewrite unsafe response or fallback to default."""

from typing import Optional

FALLBACK_RESPONSE = (
    "I'm unable to process this request. For assistance, please contact our support team "
    "at support@bank.com or call our helpline."
)


def _get_llm():
    """Lazy import."""
    from langchain_openai import ChatOpenAI
    from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
    if not OPENAI_API_KEY:
        return None
    return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.0)


def rewrite_safe(response: str, user_message: str, reason: Optional[str] = None) -> Optional[str]:
    """
    Attempt to rewrite the response to be safe and professional.
    Returns rewritten text, or None if rewrite fails.
    """
    llm = _get_llm()
    if not llm:
        return None

    reason_note = f" (Issue: {reason})" if reason else ""

    prompt = """Rewrite this banking support response to be safe and professional.
Remove any promises of actions not performed, any sensitive data, and ensure professional tone.
Keep the helpful intent but make it accurate and compliant.

User asked: "{user_msg}"
Original response: "{response}"{reason_note}

Return ONLY the rewritten response, nothing else.""".format(
        user_msg=user_message.replace('"', "'")[:200],
        response=response.replace('"', "'")[:600],
        reason_note=reason_note,
    )

    try:
        resp = llm.invoke(prompt)
        rewritten = (resp.content if hasattr(resp, "content") else str(resp)).strip()
        if rewritten and len(rewritten) > 10:
            return rewritten
    except Exception:
        pass
    return None


def get_safe_response(
    response: str,
    user_message: str,
    flagged_reason: Optional[str] = None,
) -> str:
    """
    Return a safe response: try rewrite first, fallback to default.
    """
    rewritten = rewrite_safe(response, user_message, flagged_reason)
    return rewritten if rewritten else FALLBACK_RESPONSE
