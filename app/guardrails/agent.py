"""Guardrails: input checks (after user message) and output checks (before any output)."""

from app.guardrails.input_checks import check_input
from app.guardrails.output_checks import check_output
from app.guardrails.safe_rewrite import FALLBACK_RESPONSE, get_safe_response


def input_guardrails_agent(state: dict) -> dict:
    """
    Validate user message immediately after load_session.
    If flagged: set final_response and guardrail_flagged → route to save_session.
    If OK: return {} (pass through to greeter).
    """
    user_message = state.get("user_message", "") or ""
    input_flagged, input_reason = check_input(user_message)
    if input_flagged:
        return {
            "final_response": FALLBACK_RESPONSE,
            "guardrail_flagged": True,
            "guardrail_reason": f"Input blocked: {input_reason}",
        }
    return {}


def output_guardrails_agent(state: dict) -> dict:
    """
    Validate final_response before save_session. Runs after greeter or specialist.
    Redact sensitive data, LLM check, safe rewrite if needed.
    """
    user_message = state.get("user_message", "") or ""
    final_response = state.get("final_response", "") or ""

    redacted, output_flagged, output_reason = check_output(final_response, user_message)

    if not output_flagged:
        return {
            "final_response": redacted,
            "guardrail_flagged": False,
            "guardrail_reason": None,
        }

    safe = get_safe_response(redacted, user_message, output_reason)
    return {
        "final_response": safe,
        "guardrail_flagged": True,
        "guardrail_reason": f"Output corrected: {output_reason}",
    }


def guardrails_agent(state: dict) -> dict:
    """
    Legacy: full guardrails (input + output). Kept for backward compatibility.
    Prefer input_guardrails_agent and output_guardrails_agent.
    """
    user_message = state.get("user_message", "") or ""
    final_response = state.get("final_response", "") or ""

    input_flagged, input_reason = check_input(user_message)
    if input_flagged:
        return {
            "final_response": FALLBACK_RESPONSE,
            "guardrail_flagged": True,
            "guardrail_reason": f"Input blocked: {input_reason}",
        }

    redacted, output_flagged, output_reason = check_output(final_response, user_message)
    if not output_flagged:
        return {
            "final_response": redacted,
            "guardrail_flagged": False,
            "guardrail_reason": None,
        }

    safe = get_safe_response(redacted, user_message, output_reason)
    return {
        "final_response": safe,
        "guardrail_flagged": True,
        "guardrail_reason": f"Output corrected: {output_reason}",
    }
