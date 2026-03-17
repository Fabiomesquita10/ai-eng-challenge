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
        """First message: asks for identification."""
        r = client.post("/chat", json={"session_id": "api-test-1", "message": "Hi, I lost my card"})
        assert r.status_code == 200
        data = r.json()
        assert data["session_id"] == "api-test-1"
        assert data["status"] == "needs_more_info"
        assert data["needs_more_info"] is True
        assert "response" in data
