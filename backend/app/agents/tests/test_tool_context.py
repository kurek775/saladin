
import pytest
from backend.app.agents._tool_context import ToolContext, get_tool_context, set_tool_context, reset_tool_context

def test_tool_context_default_value():
    """Test that get_tool_context returns a default ToolContext when nothing is set."""
    # Store current context to restore later, ensuring a clean slate for this test.
    # This handles cases where other tests might have left a context set.
    original_context_token = set_tool_context(ToolContext())

    context = get_tool_context()
    assert context.task_id == ""
    assert context.agent_id == ""

    reset_tool_context(original_context_token)

def test_set_and_get_tool_context():
    """Test setting and getting a ToolContext."""
    new_context = ToolContext(task_id="test_task_123", agent_id="test_agent_456")
    token = set_tool_context(new_context)
    
    retrieved_context = get_tool_context()
    assert retrieved_context == new_context
    assert retrieved_context.task_id == "test_task_123"
    assert retrieved_context.agent_id == "test_agent_456"
    
    reset_tool_context(token)

def test_reset_tool_context():
    """Test that resetting the context restores the previous state."""
    # Store initial state
    initial_context_token = set_tool_context(ToolContext(task_id="initial_task", agent_id="initial_agent"))
    initial_context = get_tool_context()

    # Set a new context
    new_context = ToolContext(task_id="new_task", agent_id="new_agent")
    new_context_token = set_tool_context(new_context)
    
    # Verify new context is active
    assert get_tool_context() == new_context

    # Reset to the context before `new_context_token` was created (i.e., `initial_context`)
    reset_tool_context(new_context_token)
    
    # Verify original context is restored
    assert get_tool_context() == initial_context

    # Clean up the initial context
    reset_tool_context(initial_context_token)

def test_tool_context_isolation_sequential():
    """Test that context is isolated and doesn't leak between different sequential settings."""
    # Store initial state
    initial_context_token = set_tool_context(ToolContext(task_id="initial", agent_id="initial_agent"))
    initial_context = get_tool_context()

    # First context
    token1 = set_tool_context(ToolContext(task_id="task_one", agent_id="agent_one"))
    assert get_tool_context().task_id == "task_one"

    # Second context (nested setting)
    token2 = set_tool_context(ToolContext(task_id="task_two", agent_id="agent_two"))
    assert get_tool_context().task_id == "task_two"

    # Reset token2, should go back to task_one
    reset_tool_context(token2)
    assert get_tool_context().task_id == "task_one"

    # Reset token1, should go back to initial
    reset_tool_context(token1)
    assert get_tool_context().task_id == "initial"

    # Clean up the initial context
    reset_tool_context(initial_context_token)
