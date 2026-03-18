"""Specialist Router: rule-based intent → specialist_route mapping."""

from typing import Literal

# intent (from Greeter) → specialist_route
INTENT_TO_ROUTE: dict[str, Literal["card", "loan", "insurance", "fraud", "premium", "general"]] = {
    "card": "card",
    "loan": "loan",
    "insurance": "insurance",
    "fraud": "fraud",
    "premium": "premium",
    "general_support": "general",
}

DEFAULT_ROUTE: Literal["general"] = "general"


def specialist_router_agent(state: dict) -> dict:
    """
    Map intent to specialist_route. Rule-based, no LLM.
    Fallback: unknown intent → general.
    """
    intent = (state.get("intent") or "").strip().lower()
    route = INTENT_TO_ROUTE.get(intent, DEFAULT_ROUTE)

    return {
        "specialist_route": route,
        "route_reason": f"intent={intent}" if intent else "intent unknown",
    }
