"""RAG pipeline: Hybrid + RRF + Rerank."""

from .rrf import rrf_merge

__all__ = ["rrf_merge"]


def get_insurance_retriever():
    """Lazy import to avoid loading heavy deps at startup."""
    from .retriever import InsuranceRetriever
    return InsuranceRetriever()
