"""General Specialist: fallback for ambiguous or general inquiries."""

from app.agents.specialists.base import generate_response


def run(state: dict) -> dict:
    """Generate response for general inquiries."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])

    system = """You are a helpful bank assistant. The customer's request wasn't clearly routed to a specific department.
Help them with general inquiries, account questions, or guide them to the right specialist if you can identify their need.
Be friendly and helpful."""
    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
