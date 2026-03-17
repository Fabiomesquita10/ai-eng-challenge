"""Routing functions for conditional edges."""

from typing import Literal


def route_after_greeter(state: dict) -> Literal["guardrails", "bouncer"]:
    """
    After Greeter: needs_more_info or identification_failed → guardrails;
    is_identified → bouncer.
    """
    if state.get("needs_more_info") or state.get("identification_failed"):
        return "guardrails"
    return "bouncer"
