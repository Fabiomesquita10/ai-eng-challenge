"""Tests for greeter agent (with mocked extraction)."""

import pytest
from unittest.mock import patch

from app.agents.greeter import greeter_agent


@pytest.fixture(autouse=True)
def mock_extraction():
    """Mock LLM extraction to avoid API calls."""
    with patch("app.agents.greeter.extract_intent", return_value=("card", 0.9)), patch(
        "app.agents.greeter.extract_identification", return_value={"name": None, "phone": None, "iban": None}
    ):
        yield


@pytest.fixture(autouse=True)
def mock_customers(test_customers):
    with patch("app.services.verification_service.get_customers", return_value=test_customers):
        yield


class TestGreeterNeedsMoreInfo:
    """When < 2 fields: needs_more_info."""

    def test_only_name_from_existing(self):
        """Existing session has name, extraction adds nothing -> still need more."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": None, "iban": None}):
            state = greeter_agent({
                "user_message": "Just checking",
                "conversation_history": [],
                "collected_data": {"name": "Fabio Mesquita", "phone": None, "iban": None},
            })
        assert state["needs_more_info"] is True
        assert state["is_identified"] is False
        assert state["identification_failed"] is False
        assert "Fabio" in state["final_response"]

    def test_only_phone(self):
        """Only phone provided -> needs more."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": "912345678", "iban": None}):
            state = greeter_agent({
                "user_message": "My phone is 912345678",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["needs_more_info"] is True
        assert state["missing_fields"] == ["name", "iban"]

    def test_only_iban(self):
        """Only IBAN provided -> needs more."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": None, "iban": "PT50000000000000000000000"}):
            state = greeter_agent({
                "user_message": "My IBAN is PT50000000000000000000000",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["needs_more_info"] is True
        assert "name" in state["missing_fields"]
        assert "phone" in state["missing_fields"]

    def test_empty_data(self):
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": None, "iban": None}):
            state = greeter_agent({
                "user_message": "Hi",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["needs_more_info"] is True
        assert "Thanks for reaching out" in state["final_response"]


class TestGreeterIdentified:
    """When 2+ fields match customer."""

    def test_name_and_phone_match(self):
        with patch("app.agents.greeter.extract_identification", return_value={"name": "Fabio Mesquita", "phone": "912345678", "iban": None}):
            state = greeter_agent({
                "user_message": "My phone is 912345678",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["is_identified"] is True
        assert state["needs_more_info"] is False
        assert state["identification_failed"] is False
        assert state["customer_record"]["name"] == "Fabio Mesquita"
        assert state["customer_record"]["premium"] is True
        assert "verified" in state["final_response"].lower()

    def test_name_and_iban_match(self):
        """Lisa: name + IBAN."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": "Lisa", "phone": None, "iban": "DE89370400440532013000"}):
            state = greeter_agent({
                "user_message": "I'm Lisa, IBAN DE89370400440532013000",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["is_identified"] is True
        assert state["customer_record"]["name"] == "Lisa"

    def test_phone_and_iban_match(self):
        """2 fields without name."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": "912345678", "iban": "PT50000000000000000000000"}):
            state = greeter_agent({
                "user_message": "Phone 912345678, IBAN PT50000000000000000000000",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["is_identified"] is True
        assert state["customer_record"]["name"] == "Fabio Mesquita"

    def test_merge_from_session_then_identify(self):
        """Existing session has name, new message adds phone -> identify."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": None, "phone": "912345678", "iban": None}):
            state = greeter_agent({
                "user_message": "My phone is 912345678",
                "conversation_history": [],
                "collected_data": {"name": "Fabio Mesquita", "phone": None, "iban": None},
            })
        assert state["is_identified"] is True
        assert state["collected_data"]["name"] == "Fabio Mesquita"
        assert state["collected_data"]["phone"] == "912345678"

    def test_output_includes_intent_and_confidence(self):
        with patch("app.agents.greeter.extract_identification", return_value={"name": "Fabio Mesquita", "phone": "912345678", "iban": None}):
            state = greeter_agent({
                "user_message": "Hi",
                "conversation_history": [],
                "collected_data": {},
            })
        assert "intent" in state
        assert "intent_confidence" in state
        assert state["intent"] == "card"  # from mock
        assert state["intent_confidence"] == 0.9


class TestGreeterIdentificationFailed:
    """When 2+ fields but no customer match."""

    def test_unknown_customer(self):
        with patch("app.agents.greeter.extract_identification", return_value={"name": "Unknown", "phone": "999999999", "iban": None}):
            state = greeter_agent({
                "user_message": "I'm Unknown, phone 999999999",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["identification_failed"] is True
        assert state["is_identified"] is False
        assert state["needs_more_info"] is False
        assert "couldn't verify" in state["final_response"].lower()

    def test_two_fields_no_match(self):
        """Name + phone but no customer in DB."""
        with patch("app.agents.greeter.extract_identification", return_value={"name": "Nobody", "phone": "000000000", "iban": None}):
            state = greeter_agent({
                "user_message": "I'm Nobody, 000000000",
                "conversation_history": [],
                "collected_data": {},
            })
        assert state["identification_failed"] is True
        assert state.get("customer_record") is None
