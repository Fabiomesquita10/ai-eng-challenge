"""Base helper for specialist response generation."""

from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

_llm: Optional[ChatOpenAI] = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        _llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.4)
    return _llm


def generate_response(
    system_prompt: str,
    user_message: str,
    conversation_history: list[dict],
    context: Optional[str] = None,
) -> str:
    """Generate specialist response using LLM."""
    llm = _get_llm()
    messages: list = [SystemMessage(content=system_prompt)]
    for turn in conversation_history[-6:]:
        content = turn.get("content", "")
        if turn.get("role") == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    if context:
        messages.append(HumanMessage(content=f"Relevant context:\n{context}\n\nCustomer message: {user_message}"))
    else:
        messages.append(HumanMessage(content=user_message))
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


def generate_response_focused(
    system_prompt: str,
    user_message: str,
    context: Optional[str] = None,
    state_summary: Optional[dict] = None,
) -> str:
    """
    Generate response with minimal input: last query + context + optional state.
    No full conversation history — reduces tokens and noise.
    """
    llm = _get_llm()
    parts = []
    if state_summary:
        summary_lines = []
        if state_summary.get("customer_type"):
            summary_lines.append(f"Customer type: {state_summary['customer_type']}")
        if state_summary.get("intent"):
            summary_lines.append(f"Intent: {state_summary['intent']}")
        if state_summary.get("name"):
            summary_lines.append(f"Customer name: {state_summary['name']}")
        if summary_lines:
            parts.append("Context about this customer:\n" + "\n".join(summary_lines) + "\n")
    if context:
        parts.append(f"Relevant knowledge:\n{context}\n")
    parts.append(f"Customer question: {user_message}")
    content = "\n".join(parts)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=content)]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)
