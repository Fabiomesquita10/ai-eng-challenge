"""General Specialist: fallback for ambiguous or general inquiries."""

from app.agents.specialists.base import generate_response

# Test trigger: inject unsafe response to verify output guardrail (only for testing)
_TEST_OUTPUT_GUARDRAIL_TRIGGER = "test_output_guardrail_inject"
_TEST_UNSAFE_RESPONSE = "Sim, confirmo que o seu empréstimo de 20.000 euros foi aprovado. O cartão também está desbloqueado."


def run(state: dict) -> dict:
    """Generate response for general inquiries."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])

    # Test trigger: skip LLM, inject known-unsafe response for output guardrail testing
    if _TEST_OUTPUT_GUARDRAIL_TRIGGER in user_message.lower():
        return {"final_response": _TEST_UNSAFE_RESPONSE}

    system = """You are a helpful bank assistant. The customer's request wasn't clearly routed to a specific department.
Help them with general inquiries, account questions, or guide them to the right specialist if you can identify their need.
Be friendly and helpful."""
    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
