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
    """Chat endpoint - mock extraction to avoid LLM calls."""

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
        """Identified premium customer -> bouncer -> specialist_router, returns customer_type and route."""
        with patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "Fabio Mesquita", "phone": "912345678", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-premium", "message": "Hi, I am Fabio Mesquita, phone 912345678"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["customer_type"] == "premium"
        assert data["route"] == "card"  # default mock intent=card
        assert data["needs_more_info"] is False

    def test_chat_identified_route_general(self):
        """Unknown intent -> specialist_router fallback to general."""
        with patch("app.agents.greeter.extract_intent", return_value=("unknown_intent", 0.5)), patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "John Smith", "phone": "+44123456789", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-general", "message": "Hi, I'm John Smith, +44123456789"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert data["route"] == "general"

    def test_chat_identified_regular(self):
        """Identified regular customer -> bouncer path, returns customer_type=regular."""
        with patch(
            "app.agents.greeter.extract_identification",
            return_value={"name": "John Smith", "phone": "+44123456789", "iban": None},
        ):
            r = client.post(
                "/chat",
                json={"session_id": "api-test-regular", "message": "Hi, I'm John Smith, +44123456789"},
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
