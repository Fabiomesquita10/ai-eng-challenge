"""Workflow nodes."""

from app.services import session_service


def load_session(state: dict) -> dict:
    """
    Load persisted session and merge with incoming message.
    Appends user_message to conversation_history.
    """
    session_id = state.get("session_id", "")
    user_message = state.get("user_message", "")

    persisted = session_service.load(session_id)

    # Merge: use persisted data, append new user turn
    conversation_history = persisted.get("conversation_history", [])
    conversation_history = conversation_history.copy()
    conversation_history.append({"role": "user", "content": user_message})

    return {
        "conversation_history": conversation_history,
        "collected_data": persisted.get("collected_data", {}),
        "customer_type": persisted.get("customer_type"),
        "specialist_route": persisted.get("specialist_route"),
    }


def greeter_agent(state: dict) -> dict:
    """
    Greeter agent (stub).
    For now: always asks for identification.
    TODO: Add extraction + verification (2/3 rule).
    """
    # Stub: always need more info, ask for phone/IBAN
    return {
        "needs_more_info": True,
        "is_identified": False,
        "identification_failed": False,
        "final_response": "Thanks for reaching out. To verify your identity, could you please provide your phone number or IBAN?",
    }


def save_session(state: dict) -> dict:
    """Persist state to session store. Appends assistant response to history."""
    session_id = state.get("session_id", "")
    final_response = state.get("final_response", "")

    # Append assistant response to conversation history for multi-turn context
    conversation_history = list(state.get("conversation_history", []))
    if final_response:
        conversation_history.append({"role": "assistant", "content": final_response})

    state_to_save = {**state, "conversation_history": conversation_history}
    session_service.save(session_id, state_to_save)
    return {}
