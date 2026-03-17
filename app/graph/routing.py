"""Routing functions for conditional edges."""

from typing import Literal

SpecialistRoute = Literal["card", "loan", "insurance", "fraud", "premium", "general"]


def route_after_greeter(state: dict) -> Literal["guardrails", "bouncer"]:
    """
    After Greeter: needs_more_info or identification_failed → guardrails;
    is_identified → bouncer.
    """
    if state.get("needs_more_info") or state.get("identification_failed"):
        return "guardrails"
    return "bouncer"


def route_after_specialist_router(state: dict) -> SpecialistRoute:
    """
    After Specialist Router: route to the specialist node based on specialist_route.
    Fallback to general if unknown.
    """
    route = state.get("specialist_route") or "general"
    valid = ("card", "loan", "insurance", "fraud", "premium", "general")
    return route if route in valid else "general"
