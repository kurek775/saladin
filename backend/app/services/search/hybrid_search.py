"""Hybrid search combining vector (ChromaDB) + keyword (BM25) with RRF merging."""

import logging
from typing import Sequence

logger = logging.getLogger(__name__)

# RRF constant — standard value from the original paper
RRF_K = 60


def rrf_merge(
    rankings: list[list[tuple[str, float]]],
    k: int = RRF_K,
) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion: score(d) = sum(1/(k + rank(d))) for each ranking.

    Each ranking is a list of (doc_id_or_text, score) already sorted by score desc.
    Returns merged list sorted by RRF score.
    """
    rrf_scores: dict[str, float] = {}

    for ranking in rankings:
        for rank, (doc, _score) in enumerate(ranking, start=1):
            rrf_scores[doc] = rrf_scores.get(doc, 0.0) + 1.0 / (k + rank)

    merged = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return merged


def hybrid_search(agent_id: str, query: str, k: int = 5) -> list[str]:
    """Run hybrid search: ChromaDB (vector) + BM25 (keyword) merged via RRF.

    Returns list of document strings sorted by relevance.
    """
    rankings: list[list[tuple[str, float]]] = []

    # Vector search via ChromaDB
    try:
        from app.services._chroma import search_chroma_with_scores
        vector_results = search_chroma_with_scores(agent_id, query, k=k * 2)
        if vector_results:
            rankings.append(vector_results)
    except (ImportError, Exception) as e:
        logger.debug("Vector search unavailable: %s", e)

    # BM25 keyword search
    try:
        from app.services.search.bm25_index import search as bm25_search
        bm25_results = bm25_search(agent_id, query, k=k * 2)
        if bm25_results:
            rankings.append(bm25_results)
    except (ImportError, Exception) as e:
        logger.debug("BM25 search unavailable: %s", e)

    if not rankings:
        # Fallback to basic ChromaDB search
        try:
            from app.services._chroma import search_chroma
            return search_chroma(agent_id, query, k)
        except (ImportError, Exception):
            return []

    merged = rrf_merge(rankings)
    return [doc for doc, _score in merged[:k]]
