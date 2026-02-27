import logging
from collections import deque

from app.services.search.hybrid_search import hybrid_search
from app.services._chroma import search_chroma, store_chroma

logger = logging.getLogger(__name__)

# In-memory fallback
# Using deque for efficient appending and popping from the left (oldest entry)
_memory_store: dict[str, deque[str]] = {}
MAX_MEMORY_ENTRIES_PER_AGENT = 100  # Arbitrary limit to prevent unbounded growth


def search_memories(agent_id: str, query: str, k: int = 5) -> list[str]:
    """Search memories for an agent using hybrid search (vector + BM25 + RRF)."""
    # Try hybrid search first
    try:
        results = hybrid_search(agent_id, query, k)
        if results:
            return results
    except Exception as e:
        logger.warning("Hybrid search failed for agent %s: %s", agent_id, e)

    # Fallback to simple ChromaDB
    try:
        return search_chroma(agent_id, query, k)
    except Exception as e:
        logger.warning("ChromaDB search failed for agent %s: %s", agent_id, e)

    # Final fallback: in-memory string match
    logger.info("Using in-memory search fallback for agent %s", agent_id)
    entries = list(_memory_store.get(agent_id, deque())) # Convert deque to list for slicing and iteration
    matches = [e for e in entries if query.lower() in e.lower()]
    return matches[:k] if matches else entries[:k]


def store_memory_entry(agent_id: str, content: str) -> None:
    """Store a memory entry for an agent."""
    try:
        store_chroma(agent_id, content)
        return
    except Exception as e:
        logger.warning("ChromaDB store failed for agent %s: %s", agent_id, e)

    if agent_id not in _memory_store:
        _memory_store[agent_id] = deque(maxlen=MAX_MEMORY_ENTRIES_PER_AGENT)
    
    _memory_store[agent_id].append(content)
