import logging

logger = logging.getLogger(__name__)

# In-memory fallback until ChromaDB is wired in Phase 5
_memory_store: dict[str, list[str]] = {}


def search_memories(agent_id: str, query: str, k: int = 5) -> list[str]:
    """Search memories for an agent. Falls back to in-memory store."""
    try:
        from app.services._chroma import search_chroma
        return search_chroma(agent_id, query, k)
    except (ImportError, Exception) as e:
        logger.debug("ChromaDB not available, using in-memory: %s", e)
        entries = _memory_store.get(agent_id, [])
        # Simple substring matching fallback
        matches = [e for e in entries if query.lower() in e.lower()]
        return matches[:k] if matches else entries[:k]


def store_memory_entry(agent_id: str, content: str) -> None:
    """Store a memory entry for an agent."""
    try:
        from app.services._chroma import store_chroma
        store_chroma(agent_id, content)
        return
    except (ImportError, Exception) as e:
        logger.debug("ChromaDB not available, using in-memory: %s", e)

    if agent_id not in _memory_store:
        _memory_store[agent_id] = []
    _memory_store[agent_id].append(content)
