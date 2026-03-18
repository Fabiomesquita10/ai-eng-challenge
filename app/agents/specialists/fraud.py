"""Fraud Specialist: fraud detection, disputes, suspicious transactions."""

from app.agents.specialists.base import generate_response


def run(state: dict) -> dict:
    """Generate response for fraud-related requests."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])

    system = """You are a fraud specialist. You help with:
- Suspicious transactions
- Disputing charges
- Unauthorized activity
- Reporting fraud

Take these matters seriously. Advise the customer to block the card if needed and guide them through the dispute process."""
    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
