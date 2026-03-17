"""LangGraph workflow with conditional routing after Greeter."""

from langgraph.graph import END, START, StateGraph

from app.graph.state import ConversationState
from .nodes import (
    bouncer_agent,
    card_specialist,
    fraud_specialist,
    general_specialist,
    guardrails_agent,
    greeter_agent,
    insurance_specialist,
    loan_specialist,
    load_session,
    premium_specialist,
    save_session,
    specialist_router,
)
from .routing import route_after_greeter, route_after_specialist_router


def _build_graph():
    builder = StateGraph(ConversationState)

    builder.add_node("load_session", load_session)
    builder.add_node("greeter_agent", greeter_agent)
    builder.add_node("guardrails", guardrails_agent)
    builder.add_node("bouncer", bouncer_agent)
    builder.add_node("specialist_router", specialist_router)
    builder.add_node("card_specialist", card_specialist)
    builder.add_node("loan_specialist", loan_specialist)
    builder.add_node("insurance_specialist", insurance_specialist)
    builder.add_node("fraud_specialist", fraud_specialist)
    builder.add_node("premium_specialist", premium_specialist)
    builder.add_node("general_specialist", general_specialist)
    builder.add_node("save_session", save_session)

    builder.add_edge(START, "load_session")
    builder.add_edge("load_session", "greeter_agent")
    builder.add_conditional_edges(
        "greeter_agent",
        route_after_greeter,
        {"guardrails": "guardrails", "bouncer": "bouncer"},
    )
    builder.add_edge("guardrails", "save_session")
    builder.add_edge("bouncer", "specialist_router")
    builder.add_conditional_edges(
        "specialist_router",
        route_after_specialist_router,
        {
            "card": "card_specialist",
            "loan": "loan_specialist",
            "insurance": "insurance_specialist",
            "fraud": "fraud_specialist",
            "premium": "premium_specialist",
            "general": "general_specialist",
        },
    )
    for specialist_node in ("card_specialist", "loan_specialist", "insurance_specialist", "fraud_specialist", "premium_specialist", "general_specialist"):
        builder.add_edge(specialist_node, "guardrails")
    builder.add_edge("save_session", END)

    return builder.compile()


graph = _build_graph()
