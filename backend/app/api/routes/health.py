# Self-improved by Saladin.
import sys
from datetime import datetime, UTC

from fastapi import APIRouter

from app.config import settings
from app.services import agent_service, task_service

router = APIRouter(tags=["health"])

# Store the application start time
start_time = datetime.now(UTC)


@router.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/api/health/details")
async def health_details() -> dict:
    uptime = str(datetime.now(UTC) - start_time)
    num_agents = agent_service.agent_count()
    num_tasks = task_service.task_count()
    python_version = sys.version
    sandbox_mode = settings.SANDBOX_MODE
    llm_provider = settings.LLM_PROVIDER
    llm_model = settings.LLM_MODEL

    return {
        "status": "ok",
        "uptime": uptime,
        "num_agents": num_agents,
        "num_tasks": num_tasks,
        "python_version": python_version,
        "sandbox_mode": sandbox_mode,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }
