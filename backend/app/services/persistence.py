"""Task persistence helpers — shared between graph nodes and services.

Extracted to break the circular dependency between task_service and graph.
Includes per-task locking to prevent race conditions on concurrent updates.
"""

import threading

from app.core.repository import get_task_repo
from app.models.domain import TaskRecord

# Per-task locks to prevent race conditions on concurrent status updates
_task_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_task_lock(task_id: str) -> threading.Lock:
    with _locks_lock:
        if task_id not in _task_locks:
            _task_locks[task_id] = threading.Lock()
        return _task_locks[task_id]


def get_task(task_id: str) -> TaskRecord | None:
    return get_task_repo().get(task_id)


def save_task(task: TaskRecord) -> None:
    """Persist a task record with per-task locking."""
    with _get_task_lock(task.id):
        get_task_repo().save(task)
