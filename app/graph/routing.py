"""Routing functions for conditional edges."""

from typing import Literal

SpecialistRoute = Literal["card", "loan", "insurance", "fraud", "premium", "general"]


def route_after_input_guardrails(state: dict) -> Literal["save_session", "greeter_agent"]:
    """
    After input guardrails: if input blocked → save_session;
    else → greeter.
    """
    if state.get("guardrail_flagged") and state.get("final_response"):
        return "save_session"
    return "greeter_agent"


def route_after_greeter(state: dict) -> Literal["output_guardrails", "bouncer"]:
    """
    After Greeter: needs_more_info or identification_failed → output_guardrails;
    is_identified → bouncer.
    """
    if state.get("needs_more_info") or state.get("identification_failed"):
        return "output_guardrails"
    return "bouncer"


def route_after_specialist_router(state: dict) -> SpecialistRoute:
    """
    After Specialist Router: route to the specialist node based on specialist_route.
    Fallback to general if unknown.
    """
    route = state.get("specialist_route") or "general"
    valid = ("card", "loan", "insurance", "fraud", "premium", "general")
    return route if route in valid else "general"
