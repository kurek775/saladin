from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.models.domain import SupervisorDecision


class WorkerResult(TypedDict):
    agent_id: str
    agent_name: str
    output: str


class ReviewResult(TypedDict):
    decision: str  # approve / reject / revise
    feedback: str


class SaladinState(TypedDict):
    task_id: str
    task_description: str
    assigned_agent_ids: list[str]
    messages: Annotated[list[BaseMessage], add_messages]
    worker_outputs: list[WorkerResult]
    supervisor_review: ReviewResult | None
    current_revision: int
    max_revisions: int
    final_output: str
    status: str
