"""Reciprocal Rank Fusion (RRF) for combining multiple ranked lists."""


def rrf_merge(
    ranked_lists: list[list[str]],
    k: int = 60,
) -> list[str]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion.

    Each document gets score = sum over lists of 1/(k + rank).
    Higher score = better. Deduplicates and returns in descending score order.

    Args:
        ranked_lists: List of lists, each inner list is [doc_id, doc_id, ...] in rank order
        k: RRF constant (default 60, common in literature)

    Returns:
        Deduplicated list of doc_ids ordered by RRF score (best first)
    """
    scores: dict[str, float] = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0.0
            scores[doc_id] += 1.0 / (k + rank)

    # Sort by score descending, return doc_ids
    sorted_docs = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return sorted_docs
