"""LangGraph workflow: load_session → greeter_agent → save_session."""

from langgraph.graph import END, START, StateGraph

from app.graph.state import ConversationState
from .nodes import greeter_agent, load_session, save_session


def _build_graph():
    builder = StateGraph(ConversationState)

    builder.add_node("load_session", load_session)
    builder.add_node("greeter_agent", greeter_agent)
    builder.add_node("save_session", save_session)

    builder.add_edge(START, "load_session")
    builder.add_edge("load_session", "greeter_agent")
    builder.add_edge("greeter_agent", "save_session")
    builder.add_edge("save_session", END)

    return builder.compile()


graph = _build_graph()
