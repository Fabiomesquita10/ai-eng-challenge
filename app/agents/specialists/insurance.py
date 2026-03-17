"""Insurance Specialist: RAG-grounded responses (Hybrid + RRF + Rerank)."""

from app.agents.specialists.base import generate_response_focused

_retriever = None


def _get_retriever():
    """Lazy import to avoid loading RAG deps at app startup."""
    global _retriever
    if _retriever is None:
        from app.rag.retriever import InsuranceRetriever
        _retriever = InsuranceRetriever()
    return _retriever


def _build_state_summary(state: dict) -> dict:
    """Build minimal state summary for focused input."""
    collected = state.get("collected_data") or {}
    return {
        "customer_type": state.get("customer_type"),
        "intent": state.get("intent"),
        "name": collected.get("name"),
    }


def run(state: dict) -> dict:
    """Generate response using RAG (Hybrid + RRF + Rerank) + LLM."""
    user_message = state.get("user_message", "")
    retriever = _get_retriever()
    chunks = retriever.retrieve(user_message)
    context = retriever.format_context(chunks) if chunks else None

    system = """You are an insurance specialist in a bank support system. Your role is to:
- Acknowledge the customer's request
- Provide clear, actionable guidance based on the knowledge provided
- Offer to connect them with the insurance support team when tailored advice is needed

Respond in a professional, supportive tone — like a bank support agent, not a generic FAQ.
If the knowledge doesn't cover their question, say so and offer to connect them with the right team.
For yacht, marine, or high-value asset insurance, mention the Specialty Insurance Support Team."""

    state_summary = _build_state_summary(state)
    response = generate_response_focused(
        system, user_message, context=context, state_summary=state_summary
    )
    return {"final_response": response}
