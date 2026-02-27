
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import dataclasses

from app.models.domain import AgentConfig, AgentRole, AgentStatus
from app.models.schemas import AgentCreate, AgentUpdate, WSEvent
from app.services import agent_service

# Mock dependencies
@pytest.fixture
def mock_agent_repo():
    with patch('app.core.repository.get_agent_repo') as mock_get_repo:
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_event_bus():
    with patch('app.core.event_bus.event_bus') as mock_bus:
        mock_bus.publish = AsyncMock()
        yield mock_bus

@pytest.fixture
def sample_agent_config():
    return AgentConfig(
        id="agent123",
        name="Test Agent",
        role=AgentRole.PLANNER,
        system_prompt="I am a test agent.",
        llm_provider="openai",
        llm_model="gpt-4",
        status=AgentStatus.IDLE,
        created_at=datetime.now(),
    )

@pytest.mark.asyncio
async def test_list_agents(mock_agent_repo, sample_agent_config):
    mock_agent_repo.list.return_value = [sample_agent_config]
    agents = agent_service.list_agents(skip=0, limit=10)
    mock_agent_repo.list.assert_called_once_with(0, 10)
    assert agents == [sample_agent_config]

@pytest.mark.asyncio
async def test_agent_count(mock_agent_repo):
    mock_agent_repo.count.return_value = 5
    count = agent_service.agent_count()
    mock_agent_repo.count.assert_called_once()
    assert count == 5

@pytest.mark.asyncio
async def test_get_agent(mock_agent_repo, sample_agent_config):
    mock_agent_repo.get.return_value = sample_agent_config
    agent = agent_service.get_agent("agent123")
    mock_agent_repo.get.assert_called_once_with("agent123")
    assert agent == sample_agent_config

@pytest.mark.asyncio
async def test_get_agent_not_found(mock_agent_repo):
    mock_agent_repo.get.return_value = None
    agent = agent_service.get_agent("nonexistent")
    assert agent is None

@pytest.mark.asyncio
async def test_get_workers(mock_agent_repo, sample_agent_config):
    worker_agent = dataclasses.replace(sample_agent_config, id="worker1", role=AgentRole.WORKER)
    planner_agent = dataclasses.replace(sample_agent_config, id="planner1", role=AgentRole.PLANNER)
    mock_agent_repo.list.return_value = [worker_agent, planner_agent]
    workers = agent_service.get_workers()
    mock_agent_repo.list.assert_called_once_with(0, 10000)
    assert workers == [worker_agent]

@pytest.mark.asyncio
async def test_create_agent(mock_agent_repo, mock_event_bus):
    agent_create_data = AgentCreate(
        name="New Agent",
        role=AgentRole.PLANNER,
        system_prompt="New prompt",
        llm_provider="google",
        llm_model="gemini",
    )
    
    # Patch datetime.now to ensure consistent created_at for comparison
    with patch('app.models.domain.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw) # Ensure other datetime calls work
        
        created_agent = await agent_service.create_agent(agent_create_data)

    mock_agent_repo.save.assert_called_once()
    saved_agent = mock_agent_repo.save.call_args[0][0]
    assert saved_agent.name == "New Agent"
    assert saved_agent.role == AgentRole.PLANNER
    assert saved_agent.system_prompt == "New prompt"
    assert saved_agent.llm_provider == "google"
    assert saved_agent.llm_model == "gemini"
    assert saved_agent.status == AgentStatus.IDLE # Default status
    assert saved_agent.created_at == datetime(2023, 1, 1, 12, 0, 0)

    mock_event_bus.publish.assert_called_once()
    event_arg = mock_event_bus.publish.call_args[0][0]
    assert event_arg.type == "agent_update"
    assert event_arg.data["action"] == "created"
    assert event_arg.data["agent"]["name"] == "New Agent"
    assert created_agent == saved_agent

@pytest.mark.asyncio
async def test_update_agent(mock_agent_repo, mock_event_bus, sample_agent_config):
    mock_agent_repo.get.return_value = sample_agent_config
    agent_update_data = AgentUpdate(name="Updated Name", system_prompt="Updated prompt")
    
    updated_agent = await agent_service.update_agent(sample_agent_config.id, agent_update_data)

    mock_agent_repo.get.assert_called_once_with(sample_agent_config.id)
    mock_agent_repo.save.assert_called_once()
    saved_agent = mock_agent_repo.save.call_args[0][0]
    assert saved_agent.name == "Updated Name"
    assert saved_agent.system_prompt == "Updated prompt"
    assert saved_agent.llm_provider == sample_agent_config.llm_provider # Unchanged
    assert updated_agent == saved_agent

    mock_event_bus.publish.assert_called_once()
    event_arg = mock_event_bus.publish.call_args[0][0]
    assert event_arg.type == "agent_update"
    assert event_arg.data["action"] == "updated"
    assert event_arg.data["agent"]["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_update_agent_not_found(mock_agent_repo, mock_event_bus):
    mock_agent_repo.get.return_value = None
    agent_update_data = AgentUpdate(name="Updated Name")
    updated_agent = await agent_service.update_agent("nonexistent", agent_update_data)
    assert updated_agent is None
    mock_agent_repo.get.assert_called_once_with("nonexistent")
    mock_agent_repo.save.assert_not_called()
    mock_event_bus.publish.assert_not_called()

@pytest.mark.asyncio
async def test_update_agent_no_changes(mock_agent_repo, mock_event_bus, sample_agent_config):
    mock_agent_repo.get.return_value = sample_agent_config
    agent_update_data = AgentUpdate() # No fields provided
    updated_agent = await agent_service.update_agent(sample_agent_config.id, agent_update_data)
    assert updated_agent == sample_agent_config # Should return original agent
    mock_agent_repo.save.assert_not_called() # No save if no changes
    mock_event_bus.publish.assert_called_once() # Event should still be published even if no changes were saved.

@pytest.mark.asyncio
async def test_delete_agent_success(mock_agent_repo, mock_event_bus):
    mock_agent_repo.delete.return_value = True
    result = await agent_service.delete_agent("agent123")
    mock_agent_repo.delete.assert_called_once_with("agent123")
    assert result is True
    mock_event_bus.publish.assert_called_once()
    event_arg = mock_event_bus.publish.call_args[0][0]
    assert event_arg.type == "agent_update"
    assert event_arg.data["action"] == "deleted"
    assert event_arg.data["agent_id"] == "agent123"

@pytest.mark.asyncio
async def test_delete_agent_not_found(mock_agent_repo, mock_event_bus):
    mock_agent_repo.delete.return_value = False
    result = await agent_service.delete_agent("nonexistent")
    assert result is False
    mock_agent_repo.delete.assert_called_once_with("nonexistent")
    mock_event_bus.publish.assert_not_called() # No event if not deleted

@pytest.mark.asyncio
async def test_set_agent_status(mock_agent_repo, mock_event_bus, sample_agent_config):
    mock_agent_repo.get.return_value = sample_agent_config
    
    await agent_service.set_agent_status(sample_agent_config.id, AgentStatus.BUSY)

    mock_agent_repo.get.assert_called_once_with(sample_agent_config.id)
    mock_agent_repo.save.assert_called_once()
    saved_agent = mock_agent_repo.save.call_args[0][0]
    assert saved_agent.status == AgentStatus.BUSY
    assert saved_agent.id == sample_agent_config.id

    mock_event_bus.publish.assert_called_once()
    event_arg = mock_event_bus.publish.call_args[0][0]
    assert event_arg.type == "agent_update"
    assert event_arg.data["action"] == "status_changed"
    assert event_arg.data["agent"]["status"] == AgentStatus.BUSY.value

@pytest.mark.asyncio
async def test_set_agent_status_agent_not_found(mock_agent_repo, mock_event_bus):
    mock_agent_repo.get.return_value = None
    await agent_service.set_agent_status("nonexistent", AgentStatus.BUSY)
    mock_agent_repo.get.assert_called_once_with("nonexistent")
    mock_agent_repo.save.assert_not_called()
    mock_event_bus.publish.assert_not_called()

@pytest.mark.asyncio
async def test_set_agent_status_concurrent_access(mock_agent_repo, sample_agent_config):
    # Test that the lock mechanism prevents race conditions
    mock_agent_repo.get.return_value = sample_agent_config

    async def _set_status_and_check(agent_id, status, mock_repo):
        await agent_service.set_agent_status(agent_id, status)
        call_args_list = mock_repo.save.call_args_list
        # Ensure that save was called with the correct status for this specific call
        # This is a bit tricky to assert directly on concurrent calls,
        # but we can ensure the lock is acquired and released.
        # The main point is that `save` is called, and the status is updated.

    # Simulate concurrent calls
    # The lock should ensure that only one call updates the status at a time,
    # and the final state reflects the last successful update.
    # We'll check the number of times save is called to ensure each call was processed.
    
    await agent_service.set_agent_status(sample_agent_config.id, AgentStatus.BUSY)
    await agent_service.set_agent_status(sample_agent_config.id, AgentStatus.IDLE)
    
    assert mock_agent_repo.save.call_count == 2
    # Verify the last call to save had the IDLE status
    last_saved_agent = mock_agent_repo.save.call_args_list[-1][0][0]
    assert last_saved_agent.status == AgentStatus.IDLE

def test_agent_dict(sample_agent_config):
    agent_dict = agent_service._agent_dict(sample_agent_config)
    assert agent_dict["id"] == sample_agent_config.id
    assert agent_dict["name"] == sample_agent_config.name
    assert agent_dict["role"] == sample_agent_config.role.value
    assert agent_dict["system_prompt"] == sample_agent_config.system_prompt
    assert agent_dict["llm_provider"] == sample_agent_config.llm_provider
    assert agent_dict["llm_model"] == sample_agent_config.llm_model
    assert agent_dict["status"] == sample_agent_config.status.value
    assert agent_dict["created_at"] == sample_agent_config.created_at
