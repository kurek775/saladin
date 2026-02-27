"""SQLModel database entities for persistent storage."""

import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class AgentDB(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = ""
    role: str = "worker"
    system_prompt: str = ""
    llm_provider: str = ""
    llm_model: str = ""
    status: str = "idle"
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class TaskDB(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    description: str = ""
    status: str = "pending"
    assigned_agents: list = Field(default_factory=list, sa_column=Column(JSON))
    current_revision: int = 0
    max_revisions: int = 3
    final_output: str = ""
    requires_human_approval: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    # Task lineage
    parent_task_id: str = ""
    depth: int = 0
    child_task_ids: list = Field(default_factory=list, sa_column=Column(JSON))
    spawned_by_agent: str = ""


class WorkerOutputDB(SQLModel, table=True):
    __tablename__ = "worker_outputs"

    id: int = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    agent_id: str = ""
    agent_name: str = ""
    output: str = ""
    revision: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class SupervisorReviewDB(SQLModel, table=True):
    __tablename__ = "supervisor_reviews"

    id: int = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    decision: str = "approve"
    feedback: str = ""
    revision: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ExecutionLogDB(SQLModel, table=True):
    __tablename__ = "execution_logs"

    id: int = Field(default=None, primary_key=True)
    task_id: str = Field(index=True)
    agent_id: Optional[str] = None
    event_type: str = ""
    message: str = ""
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
