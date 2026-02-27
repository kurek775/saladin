import asyncio
import logging
from datetime import datetime, UTC

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from app.agents.state import SaladinState, WorkerResult
from app.agents.supervisor import supervisor_review
from app.agents.worker import create_worker_agent
from app.agents.callbacks_telemetry import TelemetryCallbackHandler
from app.models.domain import (
    TaskRecord, TaskStatus, WorkerOutput, SupervisorReview, SupervisorDecision,
)
from app.models.schemas import WSEvent
from app.core.event_bus import event_bus
from app.services.agent_service import set_agent_status, get_agent
from app.services.persistence import get_task, save_task
from app.models.domain import AgentStatus

logger = logging.getLogger(__name__)


# ── Helper functions for task mutation via service layer ──

def _persist_worker_outputs(task_id: str, results: list[WorkerResult], revision: int) -> None:
    task = get_task(task_id)
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
        save_task(task)


def _persist_supervisor_review(task_id: str, review: dict, revision: int) -> None:
    task = get_task(task_id)
    if task:
        task.supervisor_reviews.append(SupervisorReview(
            decision=SupervisorDecision(review["decision"]),
            feedback=review["feedback"],
            revision=revision,
        ))
        task.updated_at = datetime.now(UTC).isoformat()
        save_task(task)


def _finalize_task(task_id: str, status: TaskStatus, final_output: str) -> None:
    task = get_task(task_id)
    if task:
        task.status = status
        task.final_output = final_output
        task.updated_at = datetime.now(UTC).isoformat()
        save_task(task)


def _update_revision(task_id: str, new_revision: int) -> None:
    task = get_task(task_id)
    if task:
        task.current_revision = new_revision
        task.status = TaskStatus.REVISION
        task.updated_at = datetime.now(UTC).isoformat()
        save_task(task)


# ── Graph Nodes ──

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
            callback = TelemetryCallbackHandler(
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

            raw_content = result["messages"][-1].content if result["messages"] else ""
            # Normalize content — some models (Gemini) return a list of blocks
            if isinstance(raw_content, list):
                output_text = "\n".join(
                    block.get("text", str(block)) if isinstance(block, dict) else str(block)
                    for block in raw_content
                )
            else:
                output_text = str(raw_content)

            await event_bus.publish(WSEvent(
                type="worker_output",
                data={
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "agent_name": agent_config.name,
                    "output": output_text[:500],
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

    logger.info(
        "dispatch_workers: task=%s revision=%d workers_ran=%d results=%d",
        task_id, revision, len(agent_ids), len(results),
    )

    # Persist worker outputs via service layer
    _persist_worker_outputs(task_id, results, revision)

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

    # Check if human-in-the-loop is required
    requires_approval = state.get("requires_human_approval", False)

    # Use the same LLM provider as the first assigned agent so the supervisor
    # doesn't fail when only a non-default provider key is available (BYOK).
    sup_provider, sup_model = "", ""
    agent_ids = state.get("assigned_agent_ids", [])
    if agent_ids:
        first_agent = get_agent(agent_ids[0])
        if first_agent:
            sup_provider = first_agent.llm_provider
            sup_model = first_agent.llm_model

    result = await supervisor_review(state, llm_provider=sup_provider, llm_model=sup_model)
    review = result["supervisor_review"]

    logger.info(
        "review_node: task=%s revision=%d decision=%s",
        task_id, state.get("current_revision", 0), review["decision"],
    )

    # Persist to task record via service layer
    _persist_supervisor_review(task_id, review, state.get("current_revision", 0))

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

    # Human-in-the-loop: interrupt if approval required
    if requires_approval:
        task = get_task(task_id)
        if task:
            task.status = TaskStatus.PENDING_HUMAN_APPROVAL
            task.updated_at = datetime.now(UTC).isoformat()
            save_task(task)

        await event_bus.publish(WSEvent(
            type="human_approval_required",
            data={
                "task_id": task_id,
                "supervisor_decision": review["decision"],
                "supervisor_feedback": review["feedback"],
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))

        try:
            from langgraph.types import interrupt
            human_decision = interrupt({
                "supervisor_decision": review["decision"],
                "supervisor_feedback": review["feedback"],
            })
            # Human override
            if isinstance(human_decision, dict) and human_decision.get("decision"):
                review = {
                    "decision": human_decision["decision"],
                    "feedback": human_decision.get("feedback", review["feedback"]),
                }
                result["supervisor_review"] = review
                # Persist the overridden review
                _persist_supervisor_review(
                    task_id, review, state.get("current_revision", 0),
                )
        except ImportError:
            logger.warning("LangGraph interrupt not available, skipping HITL")

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
            return "approve"
        return "revise"
    else:  # reject
        return "reject"


async def approve_node(state: SaladinState) -> dict:
    """Finalize task as approved."""
    task_id = state["task_id"]
    logger.info("approve_node: task=%s", task_id)
    outputs = state.get("worker_outputs", [])
    final = "\n\n".join(
        wo["output"] if isinstance(wo["output"], str) else str(wo["output"])
        for wo in outputs
    ) if outputs else ""

    _finalize_task(task_id, TaskStatus.APPROVED, final)

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "completed", "task": {"id": task_id, "status": "approved"}},
    ))

    return {"final_output": final, "status": "approved"}


async def reject_node(state: SaladinState) -> dict:
    """Finalize task as rejected."""
    task_id = state["task_id"]
    logger.info("reject_node: task=%s", task_id)
    review = state.get("supervisor_review", {})
    final = review.get("feedback", "Rejected by supervisor")

    _finalize_task(task_id, TaskStatus.REJECTED, final)

    await event_bus.publish(WSEvent(
        type="task_update",
        data={"action": "completed", "task": {"id": task_id, "status": "rejected"}},
    ))

    return {"final_output": final, "status": "rejected"}


async def revise_node(state: SaladinState) -> dict:
    """Increment revision counter before re-dispatching to workers."""
    task_id = state["task_id"]
    new_revision = state.get("current_revision", 0) + 1

    _update_revision(task_id, new_revision)

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


# ── Graph Builder ──

def build_graph(checkpointer=None) -> StateGraph:
    """Build the Saladin orchestration graph."""
    graph = StateGraph(SaladinState)

    graph.add_node("dispatch_workers", dispatch_workers)
    graph.add_node("review", review_node)
    graph.add_node("approve", approve_node)
    graph.add_node("reject", reject_node)
    graph.add_node("revise", revise_node)

    graph.set_entry_point("dispatch_workers")

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

    return graph.compile(checkpointer=checkpointer)


def _get_checkpointer():
    """Get PostgresSaver checkpointer when using postgres backend."""
    from app.config import settings
    if settings.STORAGE_BACKEND == "postgres":
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            return PostgresSaver.from_conn_string(settings.DATABASE_URL)
        except (ImportError, Exception) as e:
            logger.warning("PostgresSaver not available: %s", e)
    return None


_compiled_graph = None
_checkpointer = None


async def run_graph(task: TaskRecord) -> None:
    """Execute the full orchestration graph for a task."""
    global _compiled_graph, _checkpointer

    if _compiled_graph is None:
        _checkpointer = _get_checkpointer()
        _compiled_graph = build_graph(checkpointer=_checkpointer)
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
        "requires_human_approval": getattr(task, 'requires_human_approval', False),
        "human_decision": None,
    }

    config = {}
    if _checkpointer:
        config["configurable"] = {"thread_id": task.id}

    from app.config import settings
    try:
        await asyncio.wait_for(
            compiled.ainvoke(initial_state, config=config if config else None),
            timeout=settings.GRAPH_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("Graph execution timed out for task %s after %ds", task.id, settings.GRAPH_TIMEOUT_SECONDS)
        _finalize_task(task.id, TaskStatus.FAILED, f"Execution timed out after {settings.GRAPH_TIMEOUT_SECONDS}s")
        raise
