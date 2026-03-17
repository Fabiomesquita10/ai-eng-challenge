"""Shared conversation state for the multi-agent workflow."""

from typing import Dict, List, Literal, Optional, TypedDict


class ConversationState(TypedDict, total=False):
    """
    State shared between all agents.

    Each agent reads from and writes to this state.
    Nodes return partial updates (only the fields they change).
    """

    # -------------------------
    # Core request data
    # -------------------------
    session_id: str
    user_message: str

    # -------------------------
    # Conversation memory
    # -------------------------
    conversation_history: List[Dict[str, str]]

    # Dados recolhidos ao longo da conversa
    collected_data: Dict[str, Optional[str]]  # name, phone, iban

    # -------------------------
    # Intent & understanding
    # -------------------------
    intent: Optional[str]
    intent_confidence: Optional[float]

    # -------------------------
    # Identification (Greeter)
    # -------------------------
    missing_fields: List[str]

    is_identified: bool
    needs_more_info: bool
    identification_failed: bool

    # Dados do cliente (se encontrado)
    customer_record: Optional[Dict]

    # -------------------------
    # Customer classification (Bouncer)
    # -------------------------
    customer_type: Optional[Literal["regular", "premium", "not_customer"]]
    priority_level: Optional[Literal["normal", "high"]]

    # -------------------------
    # Routing (Specialist Router)
    # -------------------------
    specialist_route: Optional[Literal["card", "loan", "insurance", "fraud", "premium", "general"]]
    route_reason: Optional[str]
    high_value_flag: bool

    # -------------------------
    # Guardrails
    # -------------------------
    guardrail_flagged: bool
    guardrail_reason: Optional[str]

    # -------------------------
    # Final response
    # -------------------------
    final_response: Optional[str]

    # Context adicional (opcional)
    resolution_context: Optional[Dict]


# Agent contracts: which fields each agent reads/writes
# ---------------------------------------------------------------------------
# load_session   reads: session_id, user_message
#                writes: conversation_history, collected_data, customer_type, specialist_route
#
# greeter_agent  reads: session_id, user_message, conversation_history, collected_data
#                writes: collected_data, intent, intent_confidence, missing_fields,
#                        is_identified, needs_more_info, identification_failed,
#                        customer_record, final_response
#
# bouncer_agent  reads: customer_record, intent
#                writes: customer_type, priority_level
#
# specialist_router reads: intent, customer_type, priority_level, high_value_flag
#                writes: specialist_route, route_reason
#
# specialists    read: intent, customer_type, specialist_route, conversation_history
#                write: final_response
#
# guardrails     read: final_response, user_message
#                write: final_response (possibly modified), guardrail_flagged, guardrail_reason
#
# save_session   reads: full state
#                writes: (persists to store, returns state unchanged)
