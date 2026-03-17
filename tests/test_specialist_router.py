"""Tests for Specialist Router agent."""

import pytest

from app.agents.specialist_router import specialist_router_agent


class TestSpecialistRouterMapping:
    """Intent → specialist_route mapping."""

    def test_card_intent(self):
        state = specialist_router_agent({"intent": "card"})
        assert state["specialist_route"] == "card"

    def test_loan_intent(self):
        state = specialist_router_agent({"intent": "loan"})
        assert state["specialist_route"] == "loan"

    def test_insurance_intent(self):
        state = specialist_router_agent({"intent": "insurance"})
        assert state["specialist_route"] == "insurance"

    def test_fraud_intent(self):
        state = specialist_router_agent({"intent": "fraud"})
        assert state["specialist_route"] == "fraud"

    def test_premium_intent(self):
        state = specialist_router_agent({"intent": "premium"})
        assert state["specialist_route"] == "premium"

    def test_general_support_intent(self):
        state = specialist_router_agent({"intent": "general_support"})
        assert state["specialist_route"] == "general"


class TestSpecialistRouterFallback:
    """Unknown intent → general."""

    def test_unknown_intent_fallback_to_general(self):
        state = specialist_router_agent({"intent": "complaint"})
        assert state["specialist_route"] == "general"

    def test_empty_intent_fallback_to_general(self):
        state = specialist_router_agent({"intent": ""})
        assert state["specialist_route"] == "general"

    def test_none_intent_fallback_to_general(self):
        state = specialist_router_agent({})
        assert state["specialist_route"] == "general"

    def test_case_insensitive(self):
        state = specialist_router_agent({"intent": "CARD"})
        assert state["specialist_route"] == "card"


class TestSpecialistRouterOutput:
    """Output fields."""

    def test_route_reason_included(self):
        state = specialist_router_agent({"intent": "loan"})
        assert "route_reason" in state
        assert "loan" in state["route_reason"]
