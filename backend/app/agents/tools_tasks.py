"""Tool: create_task — allows agents to spawn follow-up tasks."""

import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
async def create_task(description: str) -> str:
    """Create a follow-up task. Use this when you discover related work that should be done separately.

    Args:
        description: A clear description of the follow-up task to create.

    Returns:
        A message indicating success (with new task ID) or an error message.
    """
    from app.agents._tool_context import get_tool_context
    from app.models.schemas import TaskCreate
    from app.services.task_service import AutoTaskError
    from app.services import task_service

    ctx = get_tool_context()
    if not ctx.task_id:
        return "Error: No task context available — cannot determine parent task."

    data = TaskCreate(
        description=description,
        parent_task_id=ctx.task_id,
        spawned_by_agent=ctx.agent_id,
    )

    try:
        task = await task_service.create_task(data)
        return f"Created follow-up task {task.id} (depth={task.depth})"
    except AutoTaskError as e:
        logger.warning("Auto-task creation blocked: %s", e)
        return f"Cannot create task: {e}"
    except Exception as e:
        logger.exception("Failed to create follow-up task: %s", e)
        return f"Error creating task: {e}"
