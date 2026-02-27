import pytest
from pydantic import ValidationError

from app.models.domain import AgentRole, AgentStatus, TaskStatus, SupervisorDecision
from app.models.schemas import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    TaskCreate,
    HumanDecision,
    WorkerOutputResponse,
    SupervisorReviewResponse,
    TaskResponse,
    TaskListResponse,
    WSEvent,
)


def test_agent_create_schema():
    # Valid data
    valid_data = {"name": "New Agent", "role": "supervisor"}
    agent = AgentCreate(**valid_data)
    assert agent.name == "New Agent"
    assert agent.role == AgentRole.SUPERVISOR
    assert agent.system_prompt == ""

    # Default values
    default_agent = AgentCreate(name="Default Agent")
    assert default_agent.role == AgentRole.WORKER

    # Invalid data - missing name
    with pytest.raises(ValidationError):
        AgentCreate(role="worker")

    # Invalid data - invalid role
    with pytest.raises(ValidationError):
        AgentCreate(name="Agent", role="invalid_role")


def test_agent_update_schema():
    # Valid data
    valid_data = {"name": "Updated Agent Name", "system_prompt": "New prompt"}
    agent_update = AgentUpdate(**valid_data)
    assert agent_update.name == "Updated Agent Name"
    assert agent_update.system_prompt == "New prompt"
    assert agent_update.llm_provider is None

    # No data (all optional)
    agent_update_empty = AgentUpdate()
    assert agent_update_empty.name is None


def test_agent_response_schema():
    # Valid data
    valid_data = {
        "id": "123",
        "name": "Agent X",
        "role": "worker",
        "system_prompt": "do task",
        "llm_provider": "openai",
        "llm_model": "gpt-4",
        "status": "idle",
        "created_at": "2023-01-01T12:00:00Z",
    }
    agent_response = AgentResponse(**valid_data)
    assert agent_response.id == "123"
    assert agent_response.role == AgentRole.WORKER
    assert agent_response.status == AgentStatus.IDLE

    # Invalid data - missing id
    with pytest.raises(ValidationError):
        AgentResponse(name="Agent X", role="worker", status="idle", created_at="2023-01-01T12:00:00Z",
                      system_prompt="do task", llm_provider="openai", llm_model="gpt-4")


def test_task_create_schema():
    # Valid data
    valid_data = {"description": "Create report", "assigned_agents": ["agent1", "agent2"]}
    task_create = TaskCreate(**valid_data)
    assert task_create.description == "Create report"
    assert task_create.assigned_agents == ["agent1", "agent2"]
    assert task_create.requires_human_approval is False

    # Default values
    default_task_create = TaskCreate(description="Simple task")
    assert default_task_create.assigned_agents == []

    # Invalid data - missing description
    with pytest.raises(ValidationError):
        TaskCreate(assigned_agents=["agent1"])


def test_human_decision_schema():
    # Valid data
    valid_data = {"decision": "approve", "feedback": "Good job"}
    human_decision = HumanDecision(**valid_data)
    assert human_decision.decision == "approve"
    assert human_decision.feedback == "Good job"

    # Invalid decision
    with pytest.raises(ValidationError):
        HumanDecision(decision="invalid", feedback="")

    # Valid decision with no feedback
    human_decision_no_feedback = HumanDecision(decision="reject")
    assert human_decision_no_feedback.decision == "reject"
    assert human_decision_no_feedback.feedback == ""


def test_worker_output_response_schema():
    valid_data = {
        "agent_id": "ag1",
        "agent_name": "Worker A",
        "output": "Final output",
        "revision": 1,
        "timestamp": "2023-01-01T13:00:00Z",
    }
    worker_output = WorkerOutputResponse(**valid_data)
    assert worker_output.agent_id == "ag1"

    with pytest.raises(ValidationError):
        WorkerOutputResponse(agent_id="ag1", agent_name="Worker A", output="Final output", revision=1)


def test_supervisor_review_response_schema():
    valid_data = {
        "decision": "approve",
        "feedback": "Looks solid",
        "revision": 1,
        "timestamp": "2023-01-01T14:00:00Z",
    }
    supervisor_review = SupervisorReviewResponse(**valid_data)
    assert supervisor_review.decision == SupervisorDecision.APPROVE

    with pytest.raises(ValidationError):
        SupervisorReviewResponse(decision="approve", feedback="Looks solid", revision=1)


def test_task_response_schema():
    valid_data = {
        "id": "task1",
        "description": "Do X",
        "status": "approved",
        "assigned_agents": ["ag1"],
        "worker_outputs": [],
        "supervisor_reviews": [],
        "current_revision": 1,
        "final_output": "Done",
        "created_at": "2023-01-01T10:00:00Z",
        "updated_at": "2023-01-01T11:00:00Z",
    }
    task_response = TaskResponse(**valid_data)
    assert task_response.id == "task1"
    assert task_response.status == TaskStatus.APPROVED

    with pytest.raises(ValidationError):
        TaskResponse(id="task1", description="Do X", status="approved", assigned_agents=["ag1"],
                     worker_outputs=[], supervisor_reviews=[], current_revision=1, final_output="Done",
                     created_at="2023-01-01T10:00:00Z")


def test_task_list_response_schema():
    valid_data = {
        "id": "task1",
        "description": "Do X",
        "status": "approved",
        "assigned_agents": ["ag1"],
        "current_revision": 1,
        "created_at": "2023-01-01T10:00:00Z",
        "updated_at": "2023-01-01T11:00:00Z",
    }
    task_list_response = TaskListResponse(**valid_data)
    assert task_list_response.id == "task1"
    assert task_list_response.status == TaskStatus.APPROVED

    with pytest.raises(ValidationError):
        TaskListResponse(id="task1", description="Do X", status="approved", assigned_agents=["ag1"],
                         current_revision=1, created_at="2023-01-01T10:00:00Z")


def test_ws_event_schema():
    valid_data = {"type": "task_update", "data": {"task_id": "123"}}
    ws_event = WSEvent(**valid_data)
    assert ws_event.type == "task_update"
    assert ws_event.data == {"task_id": "123"}

    with pytest.raises(ValidationError):
        WSEvent(type="task_update")

    with pytest.raises(ValidationError):
        WSEvent(data={})
