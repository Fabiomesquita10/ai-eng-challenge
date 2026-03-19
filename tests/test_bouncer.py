"""Tests for Bouncer agent."""

import pytest
from unittest.mock import patch

from app.agents.bouncer import bouncer_agent


class TestBouncerPremium:
    """Premium customers get customer_type=premium, priority_level=high."""

    def test_premium_from_customer_record(self):
        state = bouncer_agent({
            "customer_record": {"name": "Fabio Mesquita", "phone": "912345678", "premium": True},
        })
        assert state["customer_type"] == "premium"
        assert state["priority_level"] == "high"

    def test_premium_explicit_true(self):
        state = bouncer_agent({
            "customer_record": {"premium": True},
        })
        assert state["customer_type"] == "premium"
        assert state["priority_level"] == "high"


class TestBouncerRegular:
    """Regular customers get customer_type=regular, priority_level=normal."""

    def test_regular_from_customer_record(self):
        state = bouncer_agent({
            "customer_record": {"name": "John Smith", "phone": "+44123456789", "premium": False},
        })
        assert state["customer_type"] == "regular"
        assert state["priority_level"] == "normal"

    def test_regular_when_premium_missing(self):
        """Missing premium key defaults to False -> regular."""
        state = bouncer_agent({
            "customer_record": {"name": "John", "phone": "123"},
        })
        assert state["customer_type"] == "regular"
        assert state["priority_level"] == "normal"

    def test_regular_when_customer_record_empty(self):
        """Empty customer_record -> regular."""
        state = bouncer_agent({})
        assert state["customer_type"] == "regular"
        assert state["priority_level"] == "normal"
