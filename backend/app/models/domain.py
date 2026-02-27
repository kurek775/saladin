from enum import Enum
from datetime import datetime, UTC
from dataclasses import dataclass, field
import uuid


class AgentRole(str, Enum):
    WORKER = "worker"
    SUPERVISOR = "supervisor"


class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    UNDER_REVIEW = "under_review"
    REVISION = "revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    PENDING_HUMAN_APPROVAL = "pending_human_approval"


class SupervisorDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"


@dataclass
class AgentConfig:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: AgentRole = AgentRole.WORKER
    system_prompt: str = ""
    llm_provider: str = ""  # empty = use global default
    llm_model: str = ""     # empty = use global default
    status: AgentStatus = AgentStatus.IDLE
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class WorkerOutput:
    agent_id: str = ""
    agent_name: str = ""
    output: str = ""
    revision: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SupervisorReview:
    decision: SupervisorDecision = SupervisorDecision.APPROVE
    feedback: str = ""
    revision: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TaskRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: list[str] = field(default_factory=list)
    worker_outputs: list[WorkerOutput] = field(default_factory=list)
    supervisor_reviews: list[SupervisorReview] = field(default_factory=list)
    current_revision: int = 0
    max_revisions: int = 3
    final_output: str = ""
    requires_human_approval: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    # Task lineage for recursive self-improvement
    parent_task_id: str = ""
    depth: int = 0
    child_task_ids: list[str] = field(default_factory=list)
    spawned_by_agent: str = ""
