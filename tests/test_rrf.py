"""Tests for RRF (Reciprocal Rank Fusion)."""

import pytest

from app.rag.rrf import rrf_merge


class TestRRFMerge:
    def test_merge_two_lists(self):
        list_a = ["a", "b", "c"]
        list_b = ["b", "a", "d"]
        result = rrf_merge([list_a, list_b])
        # b appears in top of both -> high score; a also; c and d lower
        assert "b" in result
        assert "a" in result
        assert "c" in result
        assert "d" in result
        assert len(result) == 4

    def test_deduplication(self):
        list_a = ["a", "b", "a"]
        list_b = ["b", "c"]
        result = rrf_merge([list_a, list_b])
        assert result.count("a") == 1
        assert result.count("b") == 1

    def test_single_list(self):
        result = rrf_merge([["x", "y", "z"]])
        assert result == ["x", "y", "z"]

    def test_doc_in_both_lists_ranks_higher(self):
        # Doc "a" in position 1 of both lists should beat "b" in position 1 of one list
        list_a = ["a", "b", "c"]
        list_b = ["a", "d", "e"]
        result = rrf_merge([list_a, list_b], k=60)
        assert result[0] == "a"
