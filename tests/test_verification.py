"""Tests for verification_service (2/3 rule)."""

import pytest
from unittest.mock import patch

from app.services.verification_service import verify_legitimacy


@pytest.fixture(autouse=True)
def mock_customers(test_customers):
    """Patch get_customers to return test data."""
    with patch("app.services.verification_service.get_customers", return_value=test_customers):
        yield


class TestVerifyLegitimacy:
    """2 out of 3 rule: name, phone, IBAN."""

    def test_name_and_phone_match(self):
        """Fabio + phone should verify."""
        ok, record = verify_legitimacy({"name": "Fabio Mesquita", "phone": "912345678", "iban": None})
        assert ok is True
        assert record["name"] == "Fabio Mesquita"
        assert record["premium"] is True

    def test_name_and_iban_match(self):
        """Lisa + IBAN should verify."""
        ok, record = verify_legitimacy({"name": "Lisa", "phone": None, "iban": "DE89370400440532013000"})
        assert ok is True
        assert record["name"] == "Lisa"

    def test_phone_and_iban_match(self):
        """Phone + IBAN (no name) should verify."""
        ok, record = verify_legitimacy({"name": None, "phone": "912345678", "iban": "PT50000000000000000000000"})
        assert ok is True
        assert record["name"] == "Fabio Mesquita"

    def test_less_than_two_fields_returns_false(self):
        """Only 1 field provided."""
        ok, record = verify_legitimacy({"name": "Fabio Mesquita", "phone": None, "iban": None})
        assert ok is False
        assert record is None

    def test_two_fields_no_match_returns_false(self):
        """2 fields but no customer match."""
        ok, record = verify_legitimacy({"name": "Unknown Person", "phone": "999999999", "iban": None})
        assert ok is False
        assert record is None

    def test_phone_normalization(self):
        """Phone with spaces/dashes should match."""
        ok, record = verify_legitimacy({"name": "Fabio Mesquita", "phone": "912 345 678", "iban": None})
        assert ok is True
        assert record["name"] == "Fabio Mesquita"

    def test_name_case_insensitive(self):
        """Name matching should be case-insensitive."""
        ok, record = verify_legitimacy({"name": "fabio mesquita", "phone": "912345678", "iban": None})
        assert ok is True

    def test_record_includes_secret_and_answer(self):
        """Verified record includes secret/answer when present."""
        ok, record = verify_legitimacy({"name": "Lisa", "phone": None, "iban": "DE89370400440532013000"})
        assert ok is True
        assert record.get("secret") == "Which is the name of my dog?"
        assert record.get("answer") == "Yoda"
