from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import TaskCreate, TaskResponse, TaskListResponse
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskListResponse])
async def list_tasks(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    tasks = task_service.list_tasks(skip=skip, limit=limit)
    return [_to_list_response(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_detail_response(task)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate):
    task = await task_service.create_task(data)
    return _to_detail_response(task)


def _to_list_response(task) -> dict:
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status,
        "assigned_agents": task.assigned_agents,
        "current_revision": task.current_revision,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def _to_detail_response(task) -> dict:
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status,
        "assigned_agents": task.assigned_agents,
        "worker_outputs": [
            {
                "agent_id": wo.agent_id,
                "agent_name": wo.agent_name,
                "output": wo.output,
                "revision": wo.revision,
                "timestamp": wo.timestamp,
            }
            for wo in task.worker_outputs
        ],
        "supervisor_reviews": [
            {
                "decision": sr.decision,
                "feedback": sr.feedback,
                "revision": sr.revision,
                "timestamp": sr.timestamp,
            }
            for sr in task.supervisor_reviews
        ],
        "current_revision": task.current_revision,
        "final_output": task.final_output,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
