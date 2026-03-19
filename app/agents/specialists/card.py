"""Card Specialist: card issues, blocking, replacement, PIN."""

from app.agents.specialists.base import generate_response


def run(state: dict) -> dict:
    """Generate response for card-related requests."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])
    customer_type = state.get("customer_type", "regular")

    system = """You are a helpful bank card specialist. You help with:
- Lost or stolen cards
- Blocking/unblocking cards
- Card replacement
- PIN reset

Be concise and professional. If the customer needs to block a card urgently, advise them to use the app or call the 24h line."""
    if customer_type == "premium":
        system += "\nThis is a premium customer — offer priority support and dedicated assistance."

    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
