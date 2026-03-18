"""Pytest fixtures."""

import pytest


@pytest.fixture
def test_customers():
    """Test customer data for verification."""
    return [
        {"name": "Lisa", "phone": "+1122334455", "iban": "DE89370400440532013000", "premium": True},
        {"name": "Fabio Mesquita", "phone": "912345678", "iban": "PT50000000000000000000000", "premium": True},
        {"name": "John Smith", "phone": "+44123456789", "iban": "GB82WEST12345698765432", "premium": False},
    ]
