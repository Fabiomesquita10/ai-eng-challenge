"""Tests for response_builder tools."""

import pytest

from app.tools.response_builder import (
    build_followup_response,
    build_identification_failure_response,
    build_identified_response,
    compute_missing_fields,
    has_minimum_identification_data,
    merge_collected_data,
)


class TestMergeCollectedData:
    def test_merge_adds_new_values(self):
        existing = {"name": "Fabio", "phone": None, "iban": None}
        new = {"name": None, "phone": "912345678", "iban": None}
        result = merge_collected_data(existing, new)
        assert result == {"name": "Fabio", "phone": "912345678", "iban": None}

    def test_merge_overrides_with_non_empty(self):
        existing = {"name": "Fabio", "phone": "111", "iban": None}
        new = {"name": "Fabio Mesquita", "phone": None, "iban": None}
        result = merge_collected_data(existing, new)
        assert result["name"] == "Fabio Mesquita"
        assert result["phone"] == "111"

    def test_merge_ignores_empty_new(self):
        existing = {"name": "Fabio", "phone": "912345678", "iban": None}
        new = {"name": None, "phone": None, "iban": None}
        result = merge_collected_data(existing, new)
        assert result == existing


class TestComputeMissingFields:
    def test_all_missing(self):
        assert compute_missing_fields({}) == ["name", "phone", "iban"]
        assert compute_missing_fields({"name": None, "phone": None, "iban": None}) == ["name", "phone", "iban"]

    def test_one_filled(self):
        assert compute_missing_fields({"name": "Fabio", "phone": None, "iban": None}) == ["phone", "iban"]

    def test_two_filled(self):
        assert compute_missing_fields({"name": "Fabio", "phone": "912", "iban": None}) == ["iban"]

    def test_all_filled(self):
        assert compute_missing_fields({"name": "Fabio", "phone": "912", "iban": "PT50"}) == []


class TestHasMinimumIdentificationData:
    def test_less_than_two_false(self):
        assert has_minimum_identification_data({"name": "Fabio", "phone": None, "iban": None}) is False
        assert has_minimum_identification_data({}) is False

    def test_two_or_more_true(self):
        assert has_minimum_identification_data({"name": "Fabio", "phone": "912", "iban": None}) is True
        assert has_minimum_identification_data({"name": "Fabio", "phone": "912", "iban": "PT50"}) is True


class TestBuildFollowupResponse:
    def test_with_name(self):
        r = build_followup_response({"name": "Fabio"}, ["phone", "iban"])
        assert "Fabio" in r
        assert "phone" in r.lower() or "iban" in r.upper()

    def test_without_name(self):
        r = build_followup_response({}, ["name", "phone", "iban"])
        assert "Thanks for reaching out" in r


class TestBuildIdentificationFailureResponse:
    def test_returns_message(self):
        r = build_identification_failure_response()
        assert "couldn't verify" in r.lower()


class TestBuildIdentifiedResponse:
    def test_with_name(self):
        assert "Fabio" in build_identified_response("Fabio")
        assert "verified" in build_identified_response("Fabio").lower()

    def test_without_name(self):
        r = build_identified_response(None)
        assert "Thanks" in r
        assert "verified" in r.lower()
