"""Tests for specialist dispatch and behaviour."""

import pytest
from unittest.mock import patch

from app.agents.specialists import run_specialist, SPECIALISTS


def _base_state(route: str, message: str = "Help me") -> dict:
    return {
        "specialist_route": route,
        "user_message": message,
        "conversation_history": [],
    }


class TestSpecialistDispatch:
    """Each specialist is dispatched correctly and returns final_response."""

    def test_dispatch_card(self):
        with patch("app.agents.specialists.card.generate_response", return_value="Card help"):
            state = run_specialist(_base_state("card", "Lost my card"))
        assert state["final_response"] == "Card help"

    def test_dispatch_loan(self):
        with patch("app.agents.specialists.loan.generate_response", return_value="Loan help"):
            state = run_specialist(_base_state("loan", "I need a mortgage"))
        assert state["final_response"] == "Loan help"

    def test_dispatch_insurance(self):
        with patch("app.agents.specialists.insurance.generate_response_focused", return_value="Insurance help"), \
             patch("app.agents.specialists.insurance._get_retriever") as mock_ret:
            mock_ret.return_value.retrieve.return_value = ["chunk1"]
            mock_ret.return_value.format_context.return_value = "chunk1"
            state = run_specialist(_base_state("insurance", "yacht insurance"))
        assert state["final_response"] == "Insurance help"

    def test_dispatch_fraud(self):
        with patch("app.agents.specialists.fraud.generate_response", return_value="Fraud help"):
            state = run_specialist(_base_state("fraud", "Suspicious transaction"))
        assert state["final_response"] == "Fraud help"

    def test_dispatch_premium(self):
        with patch("app.agents.specialists.premium.generate_response", return_value="Premium help"):
            state = run_specialist(_base_state("premium", "Wealth management"))
        assert state["final_response"] == "Premium help"

    def test_dispatch_general(self):
        with patch("app.agents.specialists.general.generate_response", return_value="General help"):
            state = run_specialist(_base_state("general", "General question"))
        assert state["final_response"] == "General help"

    def test_fallback_when_route_unknown(self):
        with patch("app.agents.specialists.general.generate_response", return_value="General help"):
            state = run_specialist({"specialist_route": "unknown", "user_message": "?", "conversation_history": []})
        assert state["final_response"] == "General help"

    def test_fallback_when_route_none(self):
        with patch("app.agents.specialists.general.generate_response", return_value="General help"):
            state = run_specialist({"specialist_route": None, "user_message": "?", "conversation_history": []})
        assert state["final_response"] == "General help"

    def test_all_routes_have_handlers(self):
        for route in ["card", "loan", "insurance", "fraud", "premium", "general"]:
            assert route in SPECIALISTS


class TestSpecialistInputs:
    """Specialists receive and use state correctly."""

    def test_card_receives_customer_type(self):
        with patch("app.agents.specialists.card.generate_response") as mock_gen:
            mock_gen.return_value = "OK"
            run_specialist({
                ** _base_state("card"),
                "customer_type": "premium",
            })
        mock_gen.assert_called_once()
        call_args = mock_gen.call_args
        assert "premium" in call_args[0][0]  # system prompt includes premium note

    def test_insurance_passes_state_summary(self):
        with patch("app.agents.specialists.insurance.generate_response_focused") as mock_gen, \
             patch("app.agents.specialists.insurance._get_retriever") as mock_ret:
            mock_gen.return_value = "OK"
            mock_ret.return_value.retrieve.return_value = []
            mock_ret.return_value.format_context.return_value = ""
            run_specialist({
                **_base_state("insurance"),
                "customer_type": "premium",
                "intent": "insurance",
                "collected_data": {"name": "Fabio"},
            })
        mock_gen.assert_called_once()
        kwargs = mock_gen.call_args[1]
        assert kwargs["state_summary"]["customer_type"] == "premium"
        assert kwargs["state_summary"]["intent"] == "insurance"
        assert kwargs["state_summary"]["name"] == "Fabio"

    def test_insurance_with_empty_context(self):
        with patch("app.agents.specialists.insurance.generate_response_focused") as mock_gen, \
             patch("app.agents.specialists.insurance._get_retriever") as mock_ret:
            mock_gen.return_value = "No context available"
            mock_ret.return_value.retrieve.return_value = []
            mock_ret.return_value.format_context.return_value = ""
            state = run_specialist(_base_state("insurance", "obscure question"))
        assert state["final_response"] == "No context available"
        mock_gen.assert_called_once()
        kwargs = mock_gen.call_args[1]
        assert kwargs["context"] is None or kwargs["context"] == ""

    def test_loan_passes_conversation_history(self):
        with patch("app.agents.specialists.loan.generate_response") as mock_gen:
            mock_gen.return_value = "OK"
            run_specialist({
                **_base_state("loan"),
                "conversation_history": [
                    {"role": "user", "content": "First msg"},
                    {"role": "assistant", "content": "First reply"},
                    {"role": "user", "content": "Follow-up"},
                ],
            })
        mock_gen.assert_called_once()
        assert mock_gen.call_args[0][2]  # conversation_history
        assert len(mock_gen.call_args[0][2]) == 3
