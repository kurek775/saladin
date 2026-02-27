import logging

logger = logging.getLogger(__name__)

# In-memory fallback
_memory_store: dict[str, list[str]] = {}


def search_memories(agent_id: str, query: str, k: int = 5) -> list[str]:
    """Search memories for an agent using hybrid search (vector + BM25 + RRF)."""
    # Try hybrid search first
    try:
        from app.services.search.hybrid_search import hybrid_search
        results = hybrid_search(agent_id, query, k)
        if results:
            return results
    except ImportError:
        logger.debug("Hybrid search module not installed")
    except Exception as e:
        logger.warning("Hybrid search failed for agent %s: %s", agent_id, e)

    # Fallback to simple ChromaDB
    try:
        from app.services._chroma import search_chroma
        return search_chroma(agent_id, query, k)
    except ImportError:
        logger.debug("ChromaDB module not installed, using in-memory fallback")
    except Exception as e:
        logger.warning("ChromaDB search failed for agent %s: %s", agent_id, e)

    # Final fallback: in-memory string match
    logger.info("Using in-memory search fallback for agent %s", agent_id)
    entries = _memory_store.get(agent_id, [])
    matches = [e for e in entries if query.lower() in e.lower()]
    return matches[:k] if matches else entries[:k]


def store_memory_entry(agent_id: str, content: str) -> None:
    """Store a memory entry for an agent."""
    try:
        from app.services._chroma import store_chroma
        store_chroma(agent_id, content)
        return
    except ImportError:
        logger.debug("ChromaDB module not installed, using in-memory fallback")
    except Exception as e:
        logger.warning("ChromaDB store failed for agent %s: %s", agent_id, e)

    if agent_id not in _memory_store:
        _memory_store[agent_id] = []
    _memory_store[agent_id].append(content)
