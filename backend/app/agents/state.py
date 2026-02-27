from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field # Import BaseModel and Field

from app.models.domain import SupervisorDecision


class WorkerResult(TypedDict):
    agent_id: str
    agent_name: str
    output: str


# Change ReviewResult to Pydantic BaseModel
class ReviewResult(BaseModel):
    decision: Literal["approve", "reject", "revise"] = Field(
        ..., description="The supervisor's decision: 'approve', 'reject', or 'revise'."
    )
    feedback: str = Field(
        default="", description="Detailed feedback from the supervisor."
    )


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
    # Phase 5: Human-in-the-Loop
    requires_human_approval: bool
    human_decision: dict | None
