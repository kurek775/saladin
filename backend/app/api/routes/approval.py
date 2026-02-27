"""Approval API — resumes interrupted graph with human decision."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import HumanDecision, TaskResponse
from app.models.domain import TaskStatus
from app.services import task_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["approval"])


@router.post("/{task_id}/approve", response_model=TaskResponse)
async def approve_task(task_id: str, data: HumanDecision):
    """Resume an interrupted graph with a human approval decision."""
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.PENDING_HUMAN_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Task is not pending human approval (status={task.status.value})",
        )

    # Resume the graph with the human decision
    try:
        from app.agents.graph import _compiled_graph, _checkpointer
        from datetime import datetime, UTC
        from app.models.domain import SupervisorReview, SupervisorDecision

        if _compiled_graph and _checkpointer:
            from langgraph.types import Command
            config = {"configurable": {"thread_id": task_id}}
            await _compiled_graph.ainvoke(
                Command(resume={
                    "decision": data.decision,
                    "feedback": data.feedback,
                }),
                config=config,
            )
        else:
            # Without checkpointer, apply decision directly
            from app.services.task_service import save_task
            from app.core.event_bus import event_bus
            from app.models.schemas import WSEvent

            # Record the human review
            task.supervisor_reviews.append(SupervisorReview(
                decision=SupervisorDecision(data.decision),
                feedback=data.feedback or "",
                revision=task.current_revision,
            ))

            if data.decision == "approve":
                task.status = TaskStatus.APPROVED
                outputs = task.worker_outputs
                task.final_output = "\n\n".join(wo.output for wo in outputs)
            elif data.decision == "reject":
                task.status = TaskStatus.REJECTED
                task.final_output = data.feedback or "Rejected by human"
            elif data.decision == "revise":
                task.status = TaskStatus.REVISION
                task.current_revision += 1
            task.updated_at = datetime.now(UTC).isoformat()
            save_task(task)

            # Broadcast the status change
            await event_bus.publish(WSEvent(
                type="task_update",
                data={
                    "action": "status_changed",
                    "task": {
                        "id": task.id,
                        "status": task.status.value,
                        "current_revision": task.current_revision,
                        "final_output": task.final_output,
                    },
                },
            ))

            # If revise, re-run the graph in background
            if data.decision == "revise":
                import asyncio
                from app.services.task_service import _run_task
                bg = asyncio.create_task(_run_task(task))
                from app.services.task_service import _running_tasks
                _running_tasks.add(bg)
                bg.add_done_callback(_running_tasks.discard)

    except Exception as e:
        logger.exception("Failed to resume graph for task %s: %s", task_id, e)
        raise HTTPException(status_code=500, detail=str(e))

    # Return updated task
    updated = task_service.get_task(task_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found after approval")

    return _to_detail_response(updated)


def _to_detail_response(task) -> dict:
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value if hasattr(task.status, 'value') else task.status,
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
                "decision": sr.decision.value if hasattr(sr.decision, 'value') else sr.decision,
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
