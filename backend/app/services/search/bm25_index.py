"""Per-agent in-memory BM25 keyword indices synced with ChromaDB."""

import logging
import re

logger = logging.getLogger(__name__)

_indices: dict[str, object] = {}  # agent_id → BM25Okapi
_corpora: dict[str, list[str]] = {}  # agent_id → original documents
_tokenized: dict[str, list[list[str]]] = {}  # agent_id → tokenized documents


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    return re.findall(r'\w+', text.lower())


def add_document(agent_id: str, content: str) -> None:
    """Add a document to the BM25 index for an agent."""
    if agent_id not in _corpora:
        _corpora[agent_id] = []
        _tokenized[agent_id] = []

    _corpora[agent_id].append(content)
    _tokenized[agent_id].append(_tokenize(content))

    # Rebuild index
    _rebuild_index(agent_id)


def _rebuild_index(agent_id: str) -> None:
    """Rebuild the BM25 index from tokenized corpus."""
    try:
        from rank_bm25 import BM25Okapi
        tokens = _tokenized.get(agent_id, [])
        if tokens:
            _indices[agent_id] = BM25Okapi(tokens)
        else:
            _indices.pop(agent_id, None)
    except ImportError:
        logger.debug("rank_bm25 not installed, BM25 search unavailable")


def search(agent_id: str, query: str, k: int = 5) -> list[tuple[str, float]]:
    """Search using BM25 keyword matching.

    Returns list of (document, score) tuples sorted by relevance.
    """
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        return []

    index = _indices.get(agent_id)
    corpus = _corpora.get(agent_id, [])
    if not index or not corpus:
        return []

    tokenized_query = _tokenize(query)
    scores = index.get_scores(tokenized_query)

    # Get top-k results
    scored_docs = [(corpus[i], float(scores[i])) for i in range(len(corpus))]
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return scored_docs[:k]


def rebuild_from_chroma(agent_id: str) -> None:
    """Rebuild BM25 index from ChromaDB documents for an agent."""
    try:
        from app.services._chroma import _get_collection
        collection = _get_collection(agent_id)
        if collection.count() == 0:
            return
        result = collection.get()
        documents = result.get("documents", [])
        if documents:
            _corpora[agent_id] = documents
            _tokenized[agent_id] = [_tokenize(doc) for doc in documents]
            _rebuild_index(agent_id)
            logger.info("Rebuilt BM25 index for agent %s (%d docs)", agent_id, len(documents))
    except Exception as e:
        logger.debug("Could not rebuild BM25 from ChromaDB for %s: %s", agent_id, e)
