import logging
import uuid

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)

_client: chromadb.ClientAPI | None = None
_collection_cache: dict[str, chromadb.Collection] = {}


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def _get_collection(agent_id: str) -> chromadb.Collection:
    if agent_id in _collection_cache:
        return _collection_cache[agent_id]
    client = _get_client()
    collection_name = f"agent_{agent_id.replace('-', '_')[:50]}"
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"agent_id": agent_id},
    )
    _collection_cache[agent_id] = collection
    return collection


def search_chroma(agent_id: str, query: str, k: int = 5) -> list[str]:
    """Search memories in ChromaDB for a specific agent."""
    try:
        collection = _get_collection(agent_id)
        if collection.count() == 0:
            return []

        results = collection.query(
            query_texts=[query],
            n_results=min(k, collection.count()),
        )

        documents = results.get("documents", [[]])[0]
        return documents
    except Exception as e:
        logger.error("ChromaDB search error: %s", e)
        return []


def store_chroma(agent_id: str, content: str) -> None:
    """Store a memory entry in ChromaDB for a specific agent."""
    try:
        collection = _get_collection(agent_id)
        doc_id = str(uuid.uuid4())
        collection.add(
            documents=[content],
            ids=[doc_id],
        )
        logger.info("Stored memory for agent %s: %s", agent_id, doc_id)
    except Exception as e:
        logger.error("ChromaDB store error: %s", e)
        raise


def shutdown_chroma() -> None:
    """Clean up ChromaDB resources."""
    global _client
    _collection_cache.clear()
    _client = None
