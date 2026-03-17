"""Tests for specialist dispatch."""

import pytest
from unittest.mock import patch

from app.agents.specialists import run_specialist, SPECIALISTS


class TestSpecialistDispatch:
    def test_dispatch_card(self):
        with patch("app.agents.specialists.card.generate_response", return_value="Card help"):
            state = run_specialist({"specialist_route": "card", "user_message": "Lost my card", "conversation_history": []})
        assert state["final_response"] == "Card help"

    def test_dispatch_insurance(self):
        with patch("app.agents.specialists.insurance.generate_response_focused", return_value="Insurance help"), \
             patch("app.agents.specialists.insurance._get_retriever") as mock_ret:
            mock_ret.return_value.retrieve.return_value = ["chunk1"]
            mock_ret.return_value.format_context.return_value = "chunk1"
            state = run_specialist({"specialist_route": "insurance", "user_message": "yacht insurance", "conversation_history": []})
        assert state["final_response"] == "Insurance help"

    def test_dispatch_general_fallback(self):
        with patch("app.agents.specialists.general.generate_response", return_value="General help"):
            state = run_specialist({"specialist_route": "unknown", "user_message": "?", "conversation_history": []})
        assert state["final_response"] == "General help"

    def test_all_routes_have_handlers(self):
        for route in ["card", "loan", "insurance", "fraud", "premium", "general"]:
            assert route in SPECIALISTS
