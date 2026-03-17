"""Tests for workflow routing logic."""

import pytest

from app.graph.routing import route_after_greeter


class TestRouteAfterGreeter:
    """Conditional routing: needs_more_info/identification_failed -> guardrails; is_identified -> bouncer."""

    def test_needs_more_info_goes_to_guardrails(self):
        assert route_after_greeter({"needs_more_info": True, "is_identified": False}) == "guardrails"

    def test_identification_failed_goes_to_guardrails(self):
        assert route_after_greeter({"identification_failed": True, "is_identified": False}) == "guardrails"

    def test_both_needs_more_and_failed_goes_to_guardrails(self):
        assert route_after_greeter({
            "needs_more_info": True,
            "identification_failed": True,
        }) == "guardrails"

    def test_is_identified_goes_to_bouncer(self):
        assert route_after_greeter({
            "is_identified": True,
            "needs_more_info": False,
            "identification_failed": False,
        }) == "bouncer"

    def test_both_set_guardrails_wins(self):
        """If both set (edge case), guardrails check runs first -> guardrails."""
        assert route_after_greeter({
            "is_identified": True,
            "needs_more_info": True,
        }) == "guardrails"
