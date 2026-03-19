"""Loan Specialist: loans, mortgages, credit."""

from app.agents.specialists.base import generate_response


def run(state: dict) -> dict:
    """Generate response for loan-related requests."""
    user_message = state.get("user_message", "")
    conversation_history = state.get("conversation_history", [])

    system = """You are a helpful loan specialist. You help with:
- Loan applications
- Mortgage inquiries
- Credit products
- Interest rates and terms

Be professional and informative. For applications, guide the customer to the next steps."""
    response = generate_response(system, user_message, conversation_history)
    return {"final_response": response}
