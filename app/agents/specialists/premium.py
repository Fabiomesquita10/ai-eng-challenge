"""Premium Specialist: VIP services, wealth management, concierge."""

from app.agents.specialists.base import generate_response


def run(state: dict) -> dict:
    """Generate response for premium/VIP requests."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])

    system = """You are a premium banking specialist. You help with:
- Wealth management
- Private banking services
- Concierge services
- Premium products and exclusive offers

This customer has premium status. Offer personalized, high-touch assistance."""
    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
