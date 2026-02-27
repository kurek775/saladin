import uuid
from datetime import datetime, UTC

import pytest

from app.models.domain import (
    AgentRole,
    AgentStatus,
    TaskStatus,
    SupervisorDecision,
    AgentConfig,
    WorkerOutput,
    SupervisorReview,
    TaskRecord,
)


def test_agent_role_enum():
    assert AgentRole.WORKER == "worker"
    assert AgentRole.SUPERVISOR == "supervisor"


def test_agent_status_enum():
    assert AgentStatus.IDLE == "idle"
    assert AgentStatus.BUSY == "busy"
    assert AgentStatus.ERROR == "error"


def test_task_status_enum():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.UNDER_REVIEW == "under_review"
    assert TaskStatus.REVISION == "revision"
    assert TaskStatus.APPROVED == "approved"
    assert TaskStatus.REJECTED == "rejected"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.PENDING_HUMAN_APPROVAL == "pending_human_approval"


def test_supervisor_decision_enum():
    assert SupervisorDecision.APPROVE == "approve"
    assert SupervisorDecision.REJECT == "reject"
    assert SupervisorDecision.REVISE == "revise"


def test_agent_config_dataclass():
    agent_config = AgentConfig(name="Test Agent", role=AgentRole.SUPERVISOR)
    assert isinstance(agent_config.id, str)
    assert uuid.UUID(agent_config.id, version=4)
    assert agent_config.name == "Test Agent"
    assert agent_config.role == AgentRole.SUPERVISOR
    assert agent_config.system_prompt == ""
    assert agent_config.llm_provider == ""
    assert agent_config.llm_model == ""
    assert agent_config.status == AgentStatus.IDLE
    assert isinstance(agent_config.created_at, str)
    assert datetime.fromisoformat(agent_config.created_at).tzinfo == UTC

    # Test default values
    default_agent_config = AgentConfig(name="Default Agent")
    assert default_agent_config.role == AgentRole.WORKER
    assert default_agent_config.status == AgentStatus.IDLE


def test_worker_output_dataclass():
    timestamp_str = datetime.now(UTC).isoformat()
    worker_output = WorkerOutput(
        agent_id=str(uuid.uuid4()),
        agent_name="Worker 1",
        output="Task output",
        revision=1,
        timestamp=timestamp_str
    )
    assert isinstance(worker_output.agent_id, str)
    assert worker_output.agent_name == "Worker 1"
    assert worker_output.output == "Task output"
    assert worker_output.revision == 1
    assert worker_output.timestamp == timestamp_str

    # Test default timestamp
    default_worker_output = WorkerOutput(agent_id="123", agent_name="Worker A", output="Output")
    assert isinstance(default_worker_output.timestamp, str)
    assert datetime.fromisoformat(default_worker_output.timestamp).tzinfo == UTC


def test_supervisor_review_dataclass():
    timestamp_str = datetime.now(UTC).isoformat()
    supervisor_review = SupervisorReview(
        decision=SupervisorDecision.REJECT,
        feedback="Needs improvement",
        revision=2,
        timestamp=timestamp_str
    )
    assert supervisor_review.decision == SupervisorDecision.REJECT
    assert supervisor_review.feedback == "Needs improvement"
    assert supervisor_review.revision == 2
    assert supervisor_review.timestamp == timestamp_str

    # Test default decision and timestamp
    default_supervisor_review = SupervisorReview()
    assert default_supervisor_review.decision == SupervisorDecision.APPROVE
    assert isinstance(default_supervisor_review.timestamp, str)
    assert datetime.fromisoformat(default_supervisor_review.timestamp).tzinfo == UTC


def test_task_record_dataclass():
    timestamp_str = datetime.now(UTC).isoformat()
    task_record = TaskRecord(
        description="Complex Task",
        status=TaskStatus.RUNNING,
        assigned_agents=["agent1", "agent2"],
        current_revision=1,
        max_revisions=5,
        requires_human_approval=True,
        created_at=timestamp_str,
        updated_at=timestamp_str,
        parent_task_id="parent123",
        depth=1,
        child_task_ids=["child456"],
        spawned_by_agent="agent1"
    )
    assert isinstance(task_record.id, str)
    assert uuid.UUID(task_record.id, version=4)
    assert task_record.description == "Complex Task"
    assert task_record.status == TaskStatus.RUNNING
    assert task_record.assigned_agents == ["agent1", "agent2"]
    assert task_record.current_revision == 1
    assert task_record.max_revisions == 5
    assert task_record.final_output == ""
    assert task_record.requires_human_approval is True
    assert task_record.created_at == timestamp_str
    assert task_record.updated_at == timestamp_str
    assert task_record.parent_task_id == "parent123"
    assert task_record.depth == 1
    assert task_record.child_task_ids == ["child456"]
    assert task_record.spawned_by_agent == "agent1"
    assert task_record.worker_outputs == []
    assert task_record.supervisor_reviews == []

    # Test default values for TaskRecord
    default_task_record = TaskRecord(description="Simple Task")
    assert default_task_record.status == TaskStatus.PENDING
    assert default_task_record.assigned_agents == []
    assert default_task_record.worker_outputs == []
    assert default_task_record.supervisor_reviews == []
    assert default_task_record.current_revision == 0
    assert default_task_record.max_revisions == 3
    assert default_task_record.final_output == ""
    assert default_task_record.requires_human_approval is False
    assert isinstance(default_task_record.created_at, str)
    assert isinstance(default_task_record.updated_at, str)
    assert datetime.fromisoformat(default_task_record.created_at).tzinfo == UTC
    assert datetime.fromisoformat(default_task_record.updated_at).tzinfo == UTC
    assert default_task_record.parent_task_id == ""
    assert default_task_record.depth == 0
    assert default_task_record.child_task_ids == []
    assert default_task_record.spawned_by_agent == ""
