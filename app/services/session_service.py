"""In-memory session storage for conversation state."""

from typing import Any

# In-memory store: session_id -> persisted state
_sessions: dict[str, dict[str, Any]] = {}


def load(session_id: str) -> dict[str, Any]:
    """Load persisted state for a session. Returns empty dict if new session."""
    return _sessions.get(session_id, {}).copy()


def save(session_id: str, state: dict[str, Any]) -> None:
    """Persist relevant fields from state for the session."""
    _sessions[session_id] = {
        "conversation_history": state.get("conversation_history", []),
        "collected_data": state.get("collected_data", {}),
        "customer_type": state.get("customer_type"),
        "specialist_route": state.get("specialist_route"),
    }


def clear(session_id: str) -> None:
    """Clear a session (for testing)."""
    if session_id in _sessions:
        del _sessions[session_id]
