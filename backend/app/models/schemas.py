from pydantic import BaseModel

from app.models.domain import AgentRole, AgentStatus, TaskStatus, SupervisorDecision


# --- Agent schemas ---

class AgentCreate(BaseModel):
    name: str
    role: AgentRole = AgentRole.WORKER
    system_prompt: str = ""
    llm_provider: str = ""
    llm_model: str = ""


class AgentUpdate(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    role: AgentRole
    system_prompt: str
    llm_provider: str
    llm_model: str
    status: AgentStatus
    created_at: str


# --- Task schemas ---

class TaskCreate(BaseModel):
    description: str
    assigned_agents: list[str] = []  # Agent IDs; empty = use all workers
    requires_human_approval: bool = False


class HumanDecision(BaseModel):
    decision: str  # approve / reject / revise
    feedback: str = ""


class WorkerOutputResponse(BaseModel):
    agent_id: str
    agent_name: str
    output: str
    revision: int
    timestamp: str


class SupervisorReviewResponse(BaseModel):
    decision: SupervisorDecision
    feedback: str
    revision: int
    timestamp: str


class TaskResponse(BaseModel):
    id: str
    description: str
    status: TaskStatus
    assigned_agents: list[str]
    worker_outputs: list[WorkerOutputResponse]
    supervisor_reviews: list[SupervisorReviewResponse]
    current_revision: int
    final_output: str
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    id: str
    description: str
    status: TaskStatus
    assigned_agents: list[str]
    current_revision: int
    created_at: str
    updated_at: str


# --- WebSocket event ---

class WSEvent(BaseModel):
    type: str  # task_update, agent_update, log, worker_output, supervisor_review, human_approval_required, telemetry
    data: dict
