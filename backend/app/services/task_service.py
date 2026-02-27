import asyncio
import logging
from datetime import datetime, UTC

from app.models.domain import TaskRecord, TaskStatus
from app.models.schemas import TaskCreate, WSEvent
from app.core.event_bus import event_bus
from app.core.key_context import RequestKeys, get_request_keys
from app.core.repository import get_task_repo
from app.services.agent_service import get_workers
from app.services.persistence import get_task, save_task  # re-export for back-compat

logger = logging.getLogger(__name__)

# Track running background tasks to prevent GC and enable monitoring
_running_tasks: set[asyncio.Task] = set()


class AutoTaskError(Exception):
    """Raised when auto-task creation safety limits are hit."""


def list_tasks(skip: int = 0, limit: int = 100) -> list[TaskRecord]:
    return get_task_repo().list(skip, limit)


def task_count() -> int:
    return get_task_repo().count()


def _validate_lineage(data: TaskCreate) -> tuple[int, str]:
    """Validate lineage constraints. Returns (depth, parent_task_id).

    Raises AutoTaskError if any safety limit is exceeded.
    """
    from app.config import settings

    if not data.parent_task_id:
        return 0, ""

    if not settings.ALLOW_AUTO_TASK_CREATION:
        raise AutoTaskError("Automatic task creation is disabled (ALLOW_AUTO_TASK_CREATION=False)")

    repo = get_task_repo()
    parent = repo.get(data.parent_task_id)
    if parent is None:
        raise AutoTaskError(f"Parent task {data.parent_task_id} not found")

    depth = parent.depth + 1
    if depth > settings.MAX_TASK_DEPTH:
        raise AutoTaskError(
            f"Max task depth ({settings.MAX_TASK_DEPTH}) exceeded — depth would be {depth}"
        )

    sibling_count = repo.count_by_parent(data.parent_task_id)
    if sibling_count >= settings.MAX_CHILD_TASKS_PER_TASK:
        raise AutoTaskError(
            f"Max children per task ({settings.MAX_CHILD_TASKS_PER_TASK}) reached for parent {data.parent_task_id}"
        )

    auto_total = repo.count_auto_created()
    if auto_total >= settings.MAX_TOTAL_AUTO_TASKS:
        raise AutoTaskError(
            f"Max total auto-created tasks ({settings.MAX_TOTAL_AUTO_TASKS}) reached"
        )

    return depth, data.parent_task_id


async def create_task(data: TaskCreate) -> TaskRecord:
    # Validate lineage safety constraints
    depth, parent_task_id = _validate_lineage(data)

    # Determine which agents to assign
    if data.assigned_agents:
        agent_ids = data.assigned_agents
    else:
        agent_ids = [a.id for a in get_workers()]

    task = TaskRecord(
        description=data.description,
        assigned_agents=agent_ids,
        parent_task_id=parent_task_id,
        depth=depth,
        spawned_by_agent=data.spawned_by_agent,
    )
    # Carry over human approval flag if present
    if hasattr(data, 'requires_human_approval') and data.requires_human_approval:
        task.requires_human_approval = True

    repo = get_task_repo()
    repo.save(task)

    # Append child ID to parent's child_task_ids
    if parent_task_id:
        parent = repo.get(parent_task_id)
        if parent:
            parent.child_task_ids.append(task.id)
            parent.updated_at = datetime.now(UTC).isoformat()
            repo.save(parent)
            await event_bus.publish(WSEvent(
                type="task_update",
                data={"action": "child_created", "task": _task_summary(parent), "child_id": task.id},
            ))

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "created", "task": _task_summary(task)},
    ))

    # Launch the graph execution in background with tracking
    from app.config import settings
    if settings.USE_QUEUE:
        await _enqueue_task(task)
    else:
        captured_keys = get_request_keys()
        bg_task = asyncio.create_task(_run_task(task, keys=captured_keys))
        _running_tasks.add(bg_task)
        bg_task.add_done_callback(_running_tasks.discard)

    return task


async def _enqueue_task(task: TaskRecord) -> None:
    """Enqueue task via ARQ when USE_QUEUE is enabled."""
    keys = get_request_keys()
    try:
        from app.core.redis_client import get_arq_pool
        pool = await get_arq_pool()
        await pool.enqueue_job(
            "execute_graph_job",
            task.id,
            keys.openai,
            keys.anthropic,
            keys.google,
        )
    except Exception as e:
        logger.error("Failed to enqueue task %s: %s", task.id, e)
        # Fallback to direct execution
        bg_task = asyncio.create_task(_run_task(task, keys=keys))
        _running_tasks.add(bg_task)
        bg_task.add_done_callback(_running_tasks.discard)


async def _run_task(task: TaskRecord, keys: RequestKeys | None = None) -> None:
    """Execute the LangGraph workflow for this task."""
    if keys is not None:
        from app.core.key_context import request_keys as _ctx
        _ctx.set(keys)

    from app.agents.graph import run_graph

    try:
        await _update_status(task, TaskStatus.RUNNING)
        await run_graph(task)
        logger.info("Graph completed successfully for task %s", task.id)
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
    get_task_repo().save(task)
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
        "parent_task_id": task.parent_task_id,
        "depth": task.depth,
        "child_task_ids": task.child_task_ids,
        "spawned_by_agent": task.spawned_by_agent,
    }
