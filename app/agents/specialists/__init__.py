"""Specialist agents: dispatch by specialist_route."""

from app.agents.specialists import card, fraud, general, insurance, loan, premium

SPECIALISTS = {
    "card": card.run,
    "loan": loan.run,
    "insurance": insurance.run,
    "fraud": fraud.run,
    "premium": premium.run,
    "general": general.run,
}


def run_specialist(state: dict) -> dict:
    """
    Dispatch to the correct specialist based on specialist_route.
    Fallback to general if route unknown.
    """
    route = state.get("specialist_route") or "general"
    if route not in SPECIALISTS:
        route = "general"
    return SPECIALISTS[route](state)
