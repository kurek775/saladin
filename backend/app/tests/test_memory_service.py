
import pytest
from unittest.mock import MagicMock, patch
from app.services import memory_service

@pytest.fixture(autouse=True)
def clear_memory_store():
    # Clear the in-memory store before each test to ensure isolation
    memory_service._memory_store.clear()
    yield
    memory_service._memory_store.clear()

@pytest.fixture
def mock_hybrid_search():
    with patch('app.services.search.hybrid_search.hybrid_search') as mock:
        yield mock

@pytest.fixture
def mock_chroma_search():
    with patch('app.services._chroma.search_chroma') as mock:
        yield mock

@pytest.fixture
def mock_chroma_store():
    with patch('app.services._chroma.store_chroma') as mock:
        yield mock

# Tests for search_memories

@pytest.mark.asyncio
async def test_search_memories_hybrid_success(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.return_value = ["hybrid result 1", "hybrid result 2"]
    results = memory_service.search_memories("agent1", "query", k=2)
    mock_hybrid_search.assert_called_once_with("agent1", "query", 2)
    mock_chroma_search.assert_not_called()
    assert results == ["hybrid result 1", "hybrid result 2"]

@pytest.mark.asyncio
async def test_search_memories_hybrid_import_error_fallback_chroma(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.return_value = ["chroma result 1"]
    results = memory_service.search_memories("agent1", "query", k=1)
    mock_hybrid_search.assert_called_once_with("agent1", "query", 1)
    mock_chroma_search.assert_called_once_with("agent1", "query", 1)
    assert results == ["chroma result 1"]

@pytest.mark.asyncio
async def test_search_memories_hybrid_exception_fallback_chroma(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = Exception("Hybrid search failed")
    mock_chroma_search.return_value = ["chroma result 1"]
    results = memory_service.search_memories("agent1", "query", k=1)
    mock_hybrid_search.assert_called_once_with("agent1", "query", 1)
    mock_chroma_search.assert_called_once_with("agent1", "query", 1)
    assert results == ["chroma result 1"]

@pytest.mark.asyncio
async def test_search_memories_chroma_success(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError # Skip hybrid
    mock_chroma_search.return_value = ["chroma result 1", "chroma result 2"]
    results = memory_service.search_memories("agent1", "query", k=2)
    mock_hybrid_search.assert_called_once_with("agent1", "query", 2)
    mock_chroma_search.assert_called_once_with("agent1", "query", 2)
    assert results == ["chroma result 1", "chroma result 2"]

@pytest.mark.asyncio
async def test_search_memories_chroma_import_error_fallback_in_memory(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    memory_service.store_memory_entry("agent1", "This is a test memory.")
    memory_service.store_memory_entry("agent1", "Another test entry.")
    results = memory_service.search_memories("agent1", "test", k=1)
    mock_hybrid_search.assert_called_once_with("agent1", "test", 1)
    mock_chroma_search.assert_called_once_with("agent1", "test", 1)
    assert results == ["This is a test memory."] # Should match first 'test' entry

@pytest.mark.asyncio
async def test_search_memories_chroma_exception_fallback_in_memory(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = Exception("Chroma search failed")
    memory_service.store_memory_entry("agent1", "This is a test memory.")
    memory_service.store_memory_entry("agent1", "Another test entry.")
    results = memory_service.search_memories("agent1", "test", k=1)
    mock_hybrid_search.assert_called_once_with("agent1", "test", 1)
    mock_chroma_search.assert_called_once_with("agent1", "test", 1)
    assert results == ["This is a test memory."]

@pytest.mark.asyncio
async def test_search_memories_in_memory_match(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    memory_service.store_memory_entry("agent1", "apple banana cherry")
    memory_service.store_memory_entry("agent1", "date elderberry fig")
    memory_service.store_memory_entry("agent1", "grape apple kiwi")
    results = memory_service.search_memories("agent1", "apple", k=2)
    assert results == ["apple banana cherry", "grape apple kiwi"]

@pytest.mark.asyncio
async def test_search_memories_in_memory_case_insensitive(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    memory_service.store_memory_entry("agent1", "Apple Pie")
    memory_service.store_memory_entry("agent1", "Red apple")
    results = memory_service.search_memories("agent1", "apple", k=2)
    assert results == ["Apple Pie", "Red apple"]

@pytest.mark.asyncio
async def test_search_memories_in_memory_no_match_returns_all(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    memory_service.store_memory_entry("agent1", "item1")
    memory_service.store_memory_entry("agent1", "item2")
    memory_service.store_memory_entry("agent1", "item3")
    results = memory_service.search_memories("agent1", "nomatch", k=2)
    assert results == ["item1", "item2"]

@pytest.mark.asyncio
async def test_search_memories_in_memory_empty_store(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    results = memory_service.search_memories("agent1", "query", k=5)
    assert results == []

@pytest.mark.asyncio
async def test_search_memories_in_memory_k_limit(mock_hybrid_search, mock_chroma_search):
    mock_hybrid_search.side_effect = ImportError
    mock_chroma_search.side_effect = ImportError
    for i in range(10):
        memory_service.store_memory_entry("agent1", f"memory {i} keyword")
    results = memory_service.search_memories("agent1", "keyword", k=3)
    assert len(results) == 3
    assert results == ["memory 0 keyword", "memory 1 keyword", "memory 2 keyword"]

# Tests for store_memory_entry

@pytest.mark.asyncio
async def test_store_memory_entry_chroma_success(mock_chroma_store):
    memory_service.store_memory_entry("agent1", "new memory")
    mock_chroma_store.assert_called_once_with("agent1", "new memory")
    assert "agent1" not in memory_service._memory_store # Should not use in-memory if chroma succeeds

@pytest.mark.asyncio
async def test_store_memory_entry_chroma_import_error_fallback_in_memory(mock_chroma_store):
    mock_chroma_store.side_effect = ImportError
    memory_service.store_memory_entry("agent1", "new memory")
    mock_chroma_store.assert_called_once_with("agent1", "new memory")
    assert memory_service._memory_store["agent1"] == ["new memory"]

@pytest.mark.asyncio
async def test_store_memory_entry_chroma_exception_fallback_in_memory(mock_chroma_store):
    mock_chroma_store.side_effect = Exception("Chroma store failed")
    memory_service.store_memory_entry("agent1", "new memory")
    mock_chroma_store.assert_called_once_with("agent1", "new memory")
    assert memory_service._memory_store["agent1"] == ["new memory"]

@pytest.mark.asyncio
async def test_store_memory_entry_in_memory_new_agent(mock_chroma_store):
    mock_chroma_store.side_effect = ImportError
    memory_service.store_memory_entry("agent_new", "first memory")
    assert memory_service._memory_store["agent_new"] == ["first memory"]

@pytest.mark.asyncio
async def test_store_memory_entry_in_memory_existing_agent(mock_chroma_store):
    mock_chroma_store.side_effect = ImportError
    memory_service._memory_store["agent_existing"] = ["old memory"]
    memory_service.store_memory_entry("agent_existing", "new memory")
    assert memory_service._memory_store["agent_existing"] == ["old memory", "new memory"]
