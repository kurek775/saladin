import asyncio
import logging
from datetime import datetime, UTC

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from app.agents.state import SaladinState, WorkerResult
from app.agents.supervisor import supervisor_review
from app.agents.worker import create_worker_agent
from app.agents.callbacks import SaladinCallbackHandler
from app.models.domain import (
    TaskRecord, TaskStatus, WorkerOutput, SupervisorReview, SupervisorDecision,
)
from app.models.schemas import WSEvent
from app.core.store import store
from app.core.event_bus import event_bus
from app.services.agent_service import set_agent_status, get_agent
from app.models.domain import AgentStatus

logger = logging.getLogger(__name__)


async def dispatch_workers(state: SaladinState) -> dict:
    """Run all assigned worker agents in parallel."""
    task_id = state["task_id"]
    agent_ids = state["assigned_agent_ids"]
    revision = state.get("current_revision", 0)
    feedback = ""

    review = state.get("supervisor_review")
    if review and review.get("feedback"):
        feedback = review["feedback"]

    results: list[WorkerResult] = []

    async def run_single_worker(agent_id: str) -> WorkerResult | None:
        agent_config = get_agent(agent_id)
        if agent_config is None:
            logger.warning("Agent %s not found, skipping", agent_id)
            return None

        await set_agent_status(agent_id, AgentStatus.BUSY)

        try:
            callback = SaladinCallbackHandler(
                task_id=task_id,
                agent_id=agent_id,
                agent_name=agent_config.name,
            )
            worker = create_worker_agent(
                agent_id=agent_id,
                custom_prompt=agent_config.system_prompt,
                revision=revision,
                revision_feedback=feedback,
                llm_provider=agent_config.llm_provider,
                llm_model=agent_config.llm_model,
            )

            task_message = state["task_description"]
            if feedback:
                task_message += f"\n\nRevision feedback: {feedback}"

            result = await worker.ainvoke(
                {"messages": [HumanMessage(content=task_message)]},
                config={"callbacks": [callback]},
            )

            # Extract the final message content
            output_text = result["messages"][-1].content if result["messages"] else ""

            await event_bus.publish(WSEvent(
                type="worker_output",
                data={
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "agent_name": agent_config.name,
                    "output": output_text[:500],  # Preview
                    "revision": revision,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            ))

            return WorkerResult(
                agent_id=agent_id,
                agent_name=agent_config.name,
                output=output_text,
            )
        except Exception as e:
            logger.exception("Worker %s failed: %s", agent_id, e)
            await set_agent_status(agent_id, AgentStatus.ERROR)
            return WorkerResult(
                agent_id=agent_id,
                agent_name=agent_config.name if agent_config else agent_id,
                output=f"Error: {e}",
            )
        finally:
            await set_agent_status(agent_id, AgentStatus.IDLE)

    # Run workers concurrently
    tasks = [run_single_worker(aid) for aid in agent_ids]
    worker_results = await asyncio.gather(*tasks)
    results = [r for r in worker_results if r is not None]

    # Persist worker outputs to the task record
    task = store.tasks.get(task_id)
    if task:
        for r in results:
            task.worker_outputs.append(WorkerOutput(
                agent_id=r["agent_id"],
                agent_name=r["agent_name"],
                output=r["output"],
                revision=revision,
            ))
        task.status = TaskStatus.UNDER_REVIEW
        task.updated_at = datetime.now(UTC).isoformat()

    await event_bus.publish(WSEvent(
        type="task_update",
        data={
            "action": "status_changed",
            "task": {"id": task_id, "status": "under_review"},
        },
    ))

    return {"worker_outputs": results, "status": "under_review"}


async def review_node(state: SaladinState) -> dict:
    """Supervisor reviews worker outputs."""
    task_id = state["task_id"]

    await event_bus.publish(WSEvent(
        type="log",
        data={
            "task_id": task_id,
            "level": "info",
            "message": "Supervisor reviewing worker outputs...",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ))

    result = await supervisor_review(state)
    review = result["supervisor_review"]

    # Persist to task record
    task = store.tasks.get(task_id)
    if task:
        task.supervisor_reviews.append(SupervisorReview(
            decision=SupervisorDecision(review["decision"]),
            feedback=review["feedback"],
            revision=state.get("current_revision", 0),
        ))
        task.updated_at = datetime.now(UTC).isoformat()

    await event_bus.publish(WSEvent(
        type="supervisor_review",
        data={
            "task_id": task_id,
            "decision": review["decision"],
            "feedback": review["feedback"],
            "revision": state.get("current_revision", 0),
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ))

    return result


def should_continue(state: SaladinState) -> str:
    """Route based on supervisor decision."""
    review = state.get("supervisor_review")
    if review is None:
        return "approve"

    decision = review["decision"]

    if decision == "approve":
        return "approve"
    elif decision == "revise":
        current = state.get("current_revision", 0)
        max_rev = state.get("max_revisions", 3)
        if current >= max_rev:
            return "approve"  # Hit max revisions, auto-approve
        return "revise"
    else:  # reject
        return "reject"


async def approve_node(state: SaladinState) -> dict:
    """Finalize task as approved."""
    task_id = state["task_id"]
    outputs = state.get("worker_outputs", [])
    final = "\n\n".join(wo["output"] for wo in outputs) if outputs else ""

    task = store.tasks.get(task_id)
    if task:
        task.status = TaskStatus.APPROVED
        task.final_output = final
        task.updated_at = datetime.now(UTC).isoformat()

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "completed", "task": {"id": task_id, "status": "approved"}},
    ))

    return {"final_output": final, "status": "approved"}


async def reject_node(state: SaladinState) -> dict:
    """Finalize task as rejected."""
    task_id = state["task_id"]
    review = state.get("supervisor_review", {})

    task = store.tasks.get(task_id)
    if task:
        task.status = TaskStatus.REJECTED
        task.final_output = review.get("feedback", "Rejected by supervisor")
        task.updated_at = datetime.now(UTC).isoformat()

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "completed", "task": {"id": task_id, "status": "rejected"}},
    ))

    return {"final_output": review.get("feedback", ""), "status": "rejected"}


async def revise_node(state: SaladinState) -> dict:
    """Increment revision counter before re-dispatching to workers."""
    task_id = state["task_id"]
    new_revision = state.get("current_revision", 0) + 1

    task = store.tasks.get(task_id)
    if task:
        task.current_revision = new_revision
        task.status = TaskStatus.REVISION
        task.updated_at = datetime.now(UTC).isoformat()

    await event_bus.publish(WSEvent(
        type="task_update",
        data={
            "action": "revision",
            "task": {"id": task_id, "status": "revision", "current_revision": new_revision},
        },
    ))
    await event_bus.publish(WSEvent(
        type="log",
        data={
            "task_id": task_id,
            "level": "info",
            "message": f"Revision {new_revision} requested. Re-dispatching workers.",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    ))

    return {"current_revision": new_revision, "status": "revision", "worker_outputs": []}


def build_graph() -> StateGraph:
    """Build the Saladin orchestration graph."""
    graph = StateGraph(SaladinState)

    # Add nodes
    graph.add_node("dispatch_workers", dispatch_workers)
    graph.add_node("review", review_node)
    graph.add_node("approve", approve_node)
    graph.add_node("reject", reject_node)
    graph.add_node("revise", revise_node)

    # Set entry point
    graph.set_entry_point("dispatch_workers")

    # Edges
    graph.add_edge("dispatch_workers", "review")
    graph.add_conditional_edges(
        "review",
        should_continue,
        {
            "approve": "approve",
            "reject": "reject",
            "revise": "revise",
        },
    )
    graph.add_edge("revise", "dispatch_workers")
    graph.add_edge("approve", END)
    graph.add_edge("reject", END)

    return graph.compile()


# Cache the compiled graph — structure is static, state is per-invocation
_compiled_graph = None


async def run_graph(task: TaskRecord) -> None:
    """Execute the full orchestration graph for a task."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    compiled = _compiled_graph

    initial_state: SaladinState = {
        "task_id": task.id,
        "task_description": task.description,
        "assigned_agent_ids": task.assigned_agents,
        "messages": [],
        "worker_outputs": [],
        "supervisor_review": None,
        "current_revision": 0,
        "max_revisions": task.max_revisions,
        "final_output": "",
        "status": "running",
    }

    await compiled.ainvoke(initial_state)
