"""Tests for FastAPI endpoints."""

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestChat:
    """Chat endpoint - mock extraction and specialists to avoid LLM calls."""

    @pytest.fixture(autouse=True)
    def mock_extraction(self):
        with patch("app.agents.greeter.extract_intent", return_value=("card", 0.9)), patch(
            "app.agents.greeter.extract_identification", return_value={"name": None, "phone": None, "iban": None}
        ):
            yield

    @pytest.fixture(autouse=True)
    def mock_customers(self, test_customers):
        with patch("app.services.verification_service.get_customers", return_value=test_customers):
            yield

    @pytest.fixture(autouse=True)
    def mock_specialists(self):
        """Mock specialists to avoid LLM calls when flow reaches a specialist."""
        mock_return = {"final_response": "Mock specialist response"}
        with (
            patch("app.agents.specialists.card.run", return_value=mock_return),
            patch("app.agents.specialists.loan.run", return_value=mock_return),
            patch("app.agents.specialists.insurance.run", return_value=mock_return),
            patch("app.agents.specialists.fraud.run", return_value=mock_return),
            patch("app.agents.specialists.premium.run", return_value=mock_return),
            patch("app.agents.specialists.general.run", return_value=mock_return),
        ):
            yield

    @pytest.fixture(autouse=True)
    def mock_guardrails(self):
        """Mock guardrails to pass through (avoid LLM calls in API flow tests)."""
        with (
            patch("app.guardrails.agent.check_input", return_value=(False, None)),
            patch(
                "app.guardrails.agent.check_output",
                side_effect=lambda r, u: (r, False, None),
            ),
        ):
            yield

    def test_chat_needs_more_info(self):
        """First message: asks for identification -> guardrails path."""
        r = client.post("/chat", json={"session_id": "api-test-1", "message": "Hi, I lost my card"})
        assert r.status_code == 200
        data = r.json()
        assert data["session_id"] == "api-test-1"
        assert data["status"] == "needs_more_info"
        assert data["needs_more_info"] is True
        assert "response" in data
        assert data.get("customer_type") is None  # Never reached bouncer

    def test_chat_identified_premium(self):
        """Identified premium customer (no secret) -> bouncer -> specialist_router."""
        with patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "DirectUserPremium", "phone": "333333333", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-premium", "message": "Hi, I am DirectUserPremium, phone 333333333"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["customer_type"] == "premium"
        assert data["route"] == "card"  # default mock intent=card
        assert data["needs_more_info"] is False

    def test_chat_identified_route_general(self):
        """Unknown intent -> specialist_router fallback to general (DirectUserRegular, no secret)."""
        with patch("app.agents.greeter.extract_intent", return_value=("unknown_intent", 0.5)), patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "DirectUserRegular", "phone": "444444444", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-general", "message": "Hi, I'm DirectUserRegular, 444444444"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["route"] == "general"

    def test_chat_identified_regular(self):
        """Identified regular customer (no secret) -> bouncer path."""
        with patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "DirectUserRegular", "phone": "444444444", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-regular", "message": "Hi, I'm DirectUserRegular, 444444444"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["customer_type"] == "regular"

    def test_chat_identification_failed(self):
        """Identification failed -> guardrails path, status=rejected."""
        with patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "Unknown", "phone": "999999999", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-failed", "message": "I'm Unknown, phone 999999999"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "rejected"
        assert data.get("customer_type") is None
