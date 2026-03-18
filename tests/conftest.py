"""Pytest fixtures."""

import pytest


@pytest.fixture
def test_customers():
    """Test customer data for verification."""
    return [
        {"name": "Lisa", "phone": "+1122334455", "iban": "DE89370400440532013000", "premium": True, "secret": "Which is the name of my dog?", "answer": "Yoda"},
        {"name": "Fabio Mesquita", "phone": "912345678", "iban": "PT50000000000000000000000", "premium": True, "secret": "What city were you born in?", "answer": "Lisbon"},
        {"name": "John Smith", "phone": "+44123456789", "iban": "GB82WEST12345698765432", "premium": False, "secret": "What is your mother's maiden name?", "answer": "Williams"},
        {"name": "DirectUser", "phone": "111111111", "iban": "PT11111111111111111111111", "premium": False},
        {"name": "DirectUserPremium", "phone": "333333333", "iban": "PT33333333333333333333333", "premium": True},
        {"name": "DirectUserRegular", "phone": "444444444", "iban": "PT44444444444444444444444", "premium": False},
    ]
