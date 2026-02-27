
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, UTC
from backend.app.agents.callbacks import SaladinCallbackHandler
from backend.app.models.schemas import WSEvent

@pytest.fixture
def mock_event_bus_publish():
    with patch('backend.app.core.event_bus.event_bus.publish', new_callable=AsyncMock) as mock_publish:
        yield mock_publish

@pytest.mark.asyncio
async def test_saladin_callback_handler_init():
    task_id = "test_task_id"
    agent_id = "test_agent_id"
    agent_name = "TestAgent"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)
    assert handler.task_id == task_id
    assert handler.agent_id == agent_id
    assert handler.agent_name == agent_name

@pytest.mark.asyncio
async def test_on_llm_start(mock_event_bus_publish):
    task_id = "test_task_id_llm_start"
    agent_id = "test_agent_id_llm_start"
    agent_name = "TestLLMAgent"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)

    await handler.on_llm_start(serialized={}, prompts=["prompt1", "prompt2"])

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.type == "log"
    assert event.data["task_id"] == task_id
    assert event.data["agent_id"] == agent_id
    assert event.data["agent_name"] == agent_name
    assert event.data["level"] == "info"
    assert event.data["message"] == f"LLM started for agent {agent_name}"
    assert "timestamp" in event.data
    # Basic check for timestamp format
    datetime.fromisoformat(event.data["timestamp"].replace("Z", "+00:00")) # Should not raise error

@pytest.mark.asyncio
async def test_on_llm_start_no_agent_name(mock_event_bus_publish):
    task_id = "test_task_id_llm_start_no_name"
    agent_id = "test_agent_id_llm_start_no_name"
    handler = SaladinCallbackHandler(task_id, agent_id)

    await handler.on_llm_start(serialized={}, prompts=["prompt1"])

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.data["message"] == "LLM started for agent supervisor"

@pytest.mark.asyncio
async def test_on_llm_end(mock_event_bus_publish):
    task_id = "test_task_id_llm_end"
    agent_id = "test_agent_id_llm_end"
    agent_name = "TestLLMAgentEnd"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)

    await handler.on_llm_end(response={"output": "some output"})

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.type == "log"
    assert event.data["task_id"] == task_id
    assert event.data["agent_id"] == agent_id
    assert event.data["agent_name"] == agent_name
    assert event.data["level"] == "info"
    assert event.data["message"] == f"LLM completed for agent {agent_name}"
    assert "timestamp" in event.data

@pytest.mark.asyncio
async def test_on_tool_start(mock_event_bus_publish):
    task_id = "test_task_id_tool_start"
    agent_id = "test_agent_id_tool_start"
    agent_name = "TestToolAgent"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)
    tool_name = "my_tool"

    await handler.on_tool_start(serialized={"name": tool_name}, input_str="tool input")

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.type == "log"
    assert event.data["task_id"] == task_id
    assert event.data["agent_id"] == agent_id
    assert event.data["agent_name"] == agent_name
    assert event.data["level"] == "info"
    assert event.data["message"] == f"Tool '{tool_name}' invoked by {agent_name}"
    assert "timestamp" in event.data

@pytest.mark.asyncio
async def test_on_tool_start_unknown_tool(mock_event_bus_publish):
    task_id = "test_task_id_tool_start_unknown"
    agent_id = "test_agent_id_tool_start_unknown"
    agent_name = "TestToolAgentUnknown"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)

    await handler.on_tool_start(serialized={}, input_str="tool input")

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.data["message"] == f"Tool 'unknown' invoked by {agent_name}"

@pytest.mark.asyncio
async def test_on_llm_error(mock_event_bus_publish):
    task_id = "test_task_id_llm_error"
    agent_id = "test_agent_id_llm_error"
    agent_name = "TestErrorAgent"
    handler = SaladinCallbackHandler(task_id, agent_id, agent_name)
    error_message = "Something went wrong with LLM"
    error = ValueError(error_message)

    await handler.on_llm_error(error=error)

    mock_event_bus_publish.assert_called_once()
    event: WSEvent = mock_event_bus_publish.call_args[0][0]
    assert event.type == "log"
    assert event.data["task_id"] == task_id
    assert event.data["agent_id"] == agent_id
    assert event.data["agent_name"] == agent_name
    assert event.data["level"] == "error"
    assert event.data["message"] == f"LLM error: {error}"
    assert "timestamp" in event.data
