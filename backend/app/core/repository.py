"""Repository pattern — abstracts storage backend (memory vs PostgreSQL)."""

from __future__ import annotations

import dataclasses
from typing import Protocol

from sqlmodel import select

from app.models.domain import (
    AgentConfig, AgentRole, AgentStatus,
    TaskRecord, TaskStatus, WorkerOutput, SupervisorReview, SupervisorDecision,
)
from app.models.database import (
    AgentDB, TaskDB, WorkerOutputDB, SupervisorReviewDB,
)
from app.core.store import store


# ── Protocols ──


class AgentRepository(Protocol):
    def list(self, skip: int = 0, limit: int = 100) -> list[AgentConfig]: ...
    def get(self, agent_id: str) -> AgentConfig | None: ...
    def save(self, agent: AgentConfig) -> None: ...
    def delete(self, agent_id: str) -> bool: ...
    def count(self) -> int: ...


class TaskRepository(Protocol):
    def list(self, skip: int = 0, limit: int = 100) -> list[TaskRecord]: ...
    def get(self, task_id: str) -> TaskRecord | None: ...
    def save(self, task: TaskRecord) -> None: ...
    def count(self) -> int: ...


# ── In-Memory Implementations ──


class InMemoryAgentRepo:
    def list(self, skip: int = 0, limit: int = 100) -> list[AgentConfig]:
        return list(store.agents.values())[skip:skip + limit]

    def get(self, agent_id: str) -> AgentConfig | None:
        return store.agents.get(agent_id)

    def save(self, agent: AgentConfig) -> None:
        store.agents[agent.id] = agent

    def delete(self, agent_id: str) -> bool:
        if agent_id in store.agents:
            del store.agents[agent_id]
            return True
        return False

    def count(self) -> int:
        return len(store.agents)


class InMemoryTaskRepo:
    def list(self, skip: int = 0, limit: int = 100) -> list[TaskRecord]:
        return list(store.tasks.values())[skip:skip + limit]

    def get(self, task_id: str) -> TaskRecord | None:
        return store.tasks.get(task_id)

    def save(self, task: TaskRecord) -> None:
        store.tasks[task.id] = task

    def count(self) -> int:
        return len(store.tasks)


# ── SQL Implementations ──


class SQLAgentRepo:
    def list(self, skip: int = 0, limit: int = 100) -> list[AgentConfig]:
        from app.core.database import get_session
        with get_session() as session:
            rows = session.exec(select(AgentDB).offset(skip).limit(limit)).all()
            return [self._to_domain(r) for r in rows]

    def get(self, agent_id: str) -> AgentConfig | None:
        from app.core.database import get_session
        with get_session() as session:
            row = session.get(AgentDB, agent_id)
            return self._to_domain(row) if row else None

    def save(self, agent: AgentConfig) -> None:
        from app.core.database import get_session
        with get_session() as session:
            existing = session.get(AgentDB, agent.id)
            if existing:
                existing.name = agent.name
                existing.role = agent.role.value
                existing.system_prompt = agent.system_prompt
                existing.llm_provider = agent.llm_provider
                existing.llm_model = agent.llm_model
                existing.status = agent.status.value
                existing.created_at = agent.created_at
            else:
                row = AgentDB(
                    id=agent.id,
                    name=agent.name,
                    role=agent.role.value,
                    system_prompt=agent.system_prompt,
                    llm_provider=agent.llm_provider,
                    llm_model=agent.llm_model,
                    status=agent.status.value,
                    created_at=agent.created_at,
                )
                session.add(row)
            session.commit()

    def delete(self, agent_id: str) -> bool:
        from app.core.database import get_session
        with get_session() as session:
            row = session.get(AgentDB, agent_id)
            if row:
                session.delete(row)
                session.commit()
                return True
            return False

    def count(self) -> int:
        from app.core.database import get_session
        with get_session() as session:
            from sqlmodel import func
            return session.exec(select(func.count()).select_from(AgentDB)).one()

    @staticmethod
    def _to_domain(row: AgentDB) -> AgentConfig:
        return AgentConfig(
            id=row.id,
            name=row.name,
            role=AgentRole(row.role),
            system_prompt=row.system_prompt,
            llm_provider=row.llm_provider,
            llm_model=row.llm_model,
            status=AgentStatus(row.status),
            created_at=row.created_at,
        )


class SQLTaskRepo:
    def list(self, skip: int = 0, limit: int = 100) -> list[TaskRecord]:
        from app.core.database import get_session
        with get_session() as session:
            rows = session.exec(select(TaskDB).offset(skip).limit(limit)).all()
            return [self._load_full(session, r) for r in rows]

    def get(self, task_id: str) -> TaskRecord | None:
        from app.core.database import get_session
        with get_session() as session:
            row = session.get(TaskDB, task_id)
            if not row:
                return None
            return self._load_full(session, row)

    def save(self, task: TaskRecord) -> None:
        from app.core.database import get_session
        with get_session() as session:
            existing = session.get(TaskDB, task.id)
            if existing:
                existing.description = task.description
                existing.status = task.status.value
                existing.assigned_agents = task.assigned_agents
                existing.current_revision = task.current_revision
                existing.max_revisions = task.max_revisions
                existing.final_output = task.final_output
                existing.requires_human_approval = getattr(task, 'requires_human_approval', False)
                existing.created_at = task.created_at
                existing.updated_at = task.updated_at
            else:
                row = TaskDB(
                    id=task.id,
                    description=task.description,
                    status=task.status.value,
                    assigned_agents=task.assigned_agents,
                    current_revision=task.current_revision,
                    max_revisions=task.max_revisions,
                    final_output=task.final_output,
                    requires_human_approval=getattr(task, 'requires_human_approval', False),
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                session.add(row)

            # Upsert worker outputs
            existing_wo_count = len(session.exec(
                select(WorkerOutputDB).where(WorkerOutputDB.task_id == task.id)
            ).all())
            for wo in task.worker_outputs[existing_wo_count:]:
                session.add(WorkerOutputDB(
                    task_id=task.id,
                    agent_id=wo.agent_id,
                    agent_name=wo.agent_name,
                    output=wo.output,
                    revision=wo.revision,
                    timestamp=wo.timestamp,
                ))

            # Upsert supervisor reviews
            existing_sr_count = len(session.exec(
                select(SupervisorReviewDB).where(SupervisorReviewDB.task_id == task.id)
            ).all())
            for sr in task.supervisor_reviews[existing_sr_count:]:
                session.add(SupervisorReviewDB(
                    task_id=task.id,
                    decision=sr.decision.value if isinstance(sr.decision, SupervisorDecision) else sr.decision,
                    feedback=sr.feedback,
                    revision=sr.revision,
                    timestamp=sr.timestamp,
                ))

            session.commit()

    def count(self) -> int:
        from app.core.database import get_session
        with get_session() as session:
            from sqlmodel import func
            return session.exec(select(func.count()).select_from(TaskDB)).one()

    def _load_full(self, session, row: TaskDB) -> TaskRecord:
        wo_rows = session.exec(
            select(WorkerOutputDB).where(WorkerOutputDB.task_id == row.id)
        ).all()
        sr_rows = session.exec(
            select(SupervisorReviewDB).where(SupervisorReviewDB.task_id == row.id)
        ).all()

        return TaskRecord(
            id=row.id,
            description=row.description,
            status=TaskStatus(row.status),
            assigned_agents=row.assigned_agents or [],
            worker_outputs=[
                WorkerOutput(
                    agent_id=wo.agent_id,
                    agent_name=wo.agent_name,
                    output=wo.output,
                    revision=wo.revision,
                    timestamp=wo.timestamp,
                )
                for wo in wo_rows
            ],
            supervisor_reviews=[
                SupervisorReview(
                    decision=SupervisorDecision(sr.decision),
                    feedback=sr.feedback,
                    revision=sr.revision,
                    timestamp=sr.timestamp,
                )
                for sr in sr_rows
            ],
            current_revision=row.current_revision,
            max_revisions=row.max_revisions,
            final_output=row.final_output,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


# ── Factory ──

_agent_repo: AgentRepository | None = None
_task_repo: TaskRepository | None = None


def get_agent_repo() -> AgentRepository:
    global _agent_repo
    if _agent_repo is None:
        from app.config import settings
        if settings.STORAGE_BACKEND == "postgres":
            _agent_repo = SQLAgentRepo()
        else:
            _agent_repo = InMemoryAgentRepo()
    return _agent_repo


def get_task_repo() -> TaskRepository:
    global _task_repo
    if _task_repo is None:
        from app.config import settings
        if settings.STORAGE_BACKEND == "postgres":
            _task_repo = SQLTaskRepo()
        else:
            _task_repo = InMemoryTaskRepo()
    return _task_repo
