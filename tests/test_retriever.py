"""Tests for InsuranceRetriever format_context."""

import pytest

pytest.importorskip("langchain_community")
pytest.importorskip("rank_bm25")

from app.rag.retriever import InsuranceRetriever


class TestFormatContext:
    """format_context cleans and limits retrieved chunks."""

    def test_empty_chunks_returns_empty(self):
        retriever = InsuranceRetriever()
        assert retriever.format_context([]) == ""

    def test_deduplicates_exact(self):
        retriever = InsuranceRetriever()
        chunks = [
            "How to lower home insurance: bundle policies and raise deductible.",
            "How to lower home insurance: bundle policies and raise deductible.",
        ]
        result = retriever.format_context(chunks)
        assert result.count("bundle policies") == 1

    def test_skips_short_fragments(self):
        retriever = InsuranceRetriever()
        chunks = [
            "Short",
            "How to lower home insurance: bundle policies and raise deductible.",
        ]
        result = retriever.format_context(chunks)
        assert "Short" not in result
        assert "bundle policies" in result

    def test_limits_total_length(self):
        retriever = InsuranceRetriever()
        long_chunk = "A" * 500
        chunks = [long_chunk] * 20
        result = retriever.format_context(chunks, max_chars=1000)
        assert len(result) <= 1100  # some overhead from separators

    def test_normalizes_separators(self):
        retriever = InsuranceRetriever()
        chunks = [
            "First chunk with enough text to pass the minimum length filter.",
            "Second chunk with enough text to pass the minimum length filter.",
        ]
        result = retriever.format_context(chunks)
        assert "---" in result  # separator between chunks
        assert "First" in result and "Second" in result
