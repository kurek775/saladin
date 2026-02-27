"""Scout endpoint — launches a self-improvement analysis task."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.schemas import TaskCreate
from app.services import task_service

router = APIRouter(prefix="/api/scout", tags=["scout"])


class ScoutLaunchRequest(BaseModel):
    num_tasks: int = Field(default=5, ge=1, le=10)
    max_depth: int = Field(default=2, ge=1, le=3)
    agent_id: str = ""


SCOUT_PROMPT_TEMPLATE = """You are a codebase scout for the Saladin self-improvement system.

Your mission:
1. Use `list_files` and `search_code` to thoroughly analyze the codebase structure, code quality, and architecture.
2. Read `IMPROVEMENTS.md` if it exists to avoid duplicating known observations.
3. Create exactly {num_tasks} follow-up tasks using the `create_task` tool. Each task should address a specific, actionable improvement you identified.

Focus areas: code quality, missing tests, error handling gaps, performance issues, security concerns, documentation, and architectural improvements.

Each child task you create will have these instructions appended:
"If you notice improvements outside your scope, use `append_improvement_note` to log them. If your fix reveals clearly related work, use `create_task` to spawn a follow-up (budget: depth {max_depth})."

Be specific in your task descriptions. Include file paths and line numbers when possible.
Max depth budget: {max_depth} — child tasks can spawn further work up to this depth limit."""


@router.post("/launch")
async def launch_scout(body: ScoutLaunchRequest):
    prompt = SCOUT_PROMPT_TEMPLATE.format(
        num_tasks=body.num_tasks,
        max_depth=body.max_depth,
    )

    assigned = [body.agent_id] if body.agent_id else []

    try:
        task = await task_service.create_task(TaskCreate(
            description=prompt,
            assigned_agents=assigned,
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "task_id": task.id,
        "status": task.status.value,
        "num_tasks": body.num_tasks,
        "max_depth": body.max_depth,
    }
