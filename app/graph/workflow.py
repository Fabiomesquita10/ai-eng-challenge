"""LangGraph workflow with conditional routing after Greeter."""

from langgraph.graph import END, START, StateGraph

from app.graph.state import ConversationState
from .nodes import (
    bouncer_agent,
    guardrails_agent,
    greeter_agent,
    load_session,
    save_session,
)
from .routing import route_after_greeter


def _build_graph():
    builder = StateGraph(ConversationState)

    builder.add_node("load_session", load_session)
    builder.add_node("greeter_agent", greeter_agent)
    builder.add_node("guardrails", guardrails_agent)
    builder.add_node("bouncer", bouncer_agent)
    builder.add_node("save_session", save_session)

    builder.add_edge(START, "load_session")
    builder.add_edge("load_session", "greeter_agent")
    builder.add_conditional_edges(
        "greeter_agent",
        route_after_greeter,
        {"guardrails": "guardrails", "bouncer": "bouncer"},
    )
    builder.add_edge("guardrails", "save_session")
    builder.add_edge("bouncer", "save_session")
    builder.add_edge("save_session", END)

    return builder.compile()


graph = _build_graph()
