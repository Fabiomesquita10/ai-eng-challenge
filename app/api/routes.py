from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.graph.workflow import graph

router = APIRouter()


def _derive_status_from_state(state: dict) -> str:
    """Map conversation state to API status."""
    if state.get("guardrail_flagged"):
        return "rejected"
    if state.get("needs_more_info"):
        return "needs_more_info"
    if state.get("customer_type") == "not_customer":
        return "rejected"
    if state.get("identification_failed"):
        return "rejected"
    if state.get("final_response"):
        return "completed"
    return "error"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user message and return the system response.

    Supports multi-turn conversation via session_id.
    """
    incoming_state = {
        "session_id": request.session_id,
        "user_message": request.message,
    }
    final_state = graph.invoke(incoming_state)
    return ChatResponse(
        session_id=final_state["session_id"],
        response=final_state.get("final_response", ""),
        status=_derive_status_from_state(final_state),
        customer_type=final_state.get("customer_type"),
        route=final_state.get("specialist_route"),
        needs_more_info=final_state.get("needs_more_info", False),
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")
