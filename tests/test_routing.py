"""Tests for workflow routing logic."""

import pytest

from app.graph.routing import (
    route_after_greeter,
    route_after_input_guardrails,
    route_after_specialist_router,
)


class TestRouteAfterInputGuardrails:
    """Input guardrails: if blocked -> save_session; else -> greeter."""

    def test_blocked_goes_to_save_session(self):
        assert route_after_input_guardrails({
            "guardrail_flagged": True,
            "final_response": "Blocked",
        }) == "save_session"

    def test_ok_goes_to_greeter(self):
        assert route_after_input_guardrails({}) == "greeter_agent"
        assert route_after_input_guardrails({"guardrail_flagged": False}) == "greeter_agent"


class TestRouteAfterGreeter:
    """Conditional routing: needs_more_info/identification_failed -> output_guardrails; is_identified -> bouncer."""

    def test_needs_more_info_goes_to_output_guardrails(self):
        assert route_after_greeter({"needs_more_info": True, "is_identified": False}) == "output_guardrails"

    def test_identification_failed_goes_to_output_guardrails(self):
        assert route_after_greeter({"identification_failed": True, "is_identified": False}) == "output_guardrails"

    def test_both_needs_more_and_failed_goes_to_output_guardrails(self):
        assert route_after_greeter({
            "needs_more_info": True,
            "identification_failed": True,
        }) == "output_guardrails"

    def test_is_identified_goes_to_bouncer(self):
        assert route_after_greeter({
            "is_identified": True,
            "needs_more_info": False,
            "identification_failed": False,
        }) == "bouncer"

    def test_both_set_output_guardrails_wins(self):
        """If both set (edge case), output_guardrails runs first."""
        assert route_after_greeter({
            "is_identified": True,
            "needs_more_info": True,
        }) == "output_guardrails"


class TestRouteAfterSpecialistRouter:
    """Conditional routing to specialist nodes."""

    def test_route_card(self):
        assert route_after_specialist_router({"specialist_route": "card"}) == "card"

    def test_route_insurance(self):
        assert route_after_specialist_router({"specialist_route": "insurance"}) == "insurance"

    def test_route_general_fallback(self):
        assert route_after_specialist_router({"specialist_route": None}) == "general"
        assert route_after_specialist_router({"specialist_route": "unknown"}) == "general"
