"""ARQ worker job for executing graph tasks asynchronously.

Run with: arq app.workers.graph_worker.WorkerSettings
"""

import logging

from app.core.key_context import RequestKeys, request_keys

logger = logging.getLogger(__name__)


async def execute_graph_job(
    ctx: dict,
    task_id: str,
    openai_key: str = "",
    anthropic_key: str = "",
    google_key: str = "",
) -> None:
    """Execute the LangGraph workflow for a task.

    Restores BYOK keys into context var before graph execution.
    """
    # Restore BYOK keys for this job
    keys = RequestKeys(openai=openai_key, anthropic=anthropic_key, google=google_key)
    token = request_keys.set(keys)

    try:
        from app.services.task_service import get_task, _run_task
        task = get_task(task_id)
        if task is None:
            logger.error("Task %s not found", task_id)
            return
        await _run_task(task)
    finally:
        request_keys.reset(token)


async def startup(ctx: dict) -> None:
    """ARQ worker startup — initialize DB if needed."""
    from app.config import settings
    if settings.STORAGE_BACKEND == "postgres":
        from app.core.database import init_db
        init_db()
    logger.info("ARQ worker started")


async def shutdown(ctx: dict) -> None:
    logger.info("ARQ worker stopped")


class WorkerSettings:
    """ARQ worker configuration."""
    functions = [execute_graph_job]
    on_startup = startup
    on_shutdown = shutdown

    # Import redis settings at runtime
    @staticmethod
    def redis_settings():
        from arq.connections import RedisSettings
        from app.config import settings
        return RedisSettings.from_dsn(settings.REDIS_URL)
