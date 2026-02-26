import asyncio
import logging
from datetime import datetime, UTC

from app.models.domain import TaskRecord, TaskStatus
from app.models.schemas import TaskCreate, WSEvent
from app.core.store import store
from app.core.event_bus import event_bus
from app.services.agent_service import get_workers

logger = logging.getLogger(__name__)

# Track running background tasks to prevent GC and enable monitoring
_running_tasks: set[asyncio.Task] = set()


def list_tasks(skip: int = 0, limit: int = 100) -> list[TaskRecord]:
    all_tasks = list(store.tasks.values())
    return all_tasks[skip:skip + limit]


def get_task(task_id: str) -> TaskRecord | None:
    return store.tasks.get(task_id)


def task_count() -> int:
    return len(store.tasks)


async def create_task(data: TaskCreate) -> TaskRecord:
    # Determine which agents to assign
    if data.assigned_agents:
        agent_ids = data.assigned_agents
    else:
        agent_ids = [a.id for a in get_workers()]

    task = TaskRecord(
        description=data.description,
        assigned_agents=agent_ids,
    )
    store.tasks[task.id] = task

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "created", "task": _task_summary(task)},
    ))

    # Launch the graph execution in background with tracking
    bg_task = asyncio.create_task(_run_task(task))
    _running_tasks.add(bg_task)
    bg_task.add_done_callback(_running_tasks.discard)

    return task


async def _run_task(task: TaskRecord) -> None:
    """Execute the LangGraph workflow for this task."""
    # Import here to avoid circular imports
    from app.agents.graph import run_graph

    try:
        await _update_status(task, TaskStatus.RUNNING)
        await run_graph(task)
    except Exception as e:
        logger.exception("Task %s failed: %s", task.id, e)
        await _update_status(task, TaskStatus.FAILED)
        await event_bus.publish(WSEvent(
            type="log",
            data={
                "task_id": task.id,
                "level": "error",
                "message": f"Task failed: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))


async def _update_status(task: TaskRecord, status: TaskStatus) -> None:
    task.status = status
    task.updated_at = datetime.now(UTC).isoformat()
    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "status_changed", "task": _task_summary(task)},
    ))


def _task_summary(task: TaskRecord) -> dict:
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value,
        "assigned_agents": task.assigned_agents,
        "current_revision": task.current_revision,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
