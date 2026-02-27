
import uuid
from datetime import datetime, UTC

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON

from app.models.database import AgentDB, TaskDB, WorkerOutputDB, SupervisorReviewDB, ExecutionLogDB


def test_agent_db_model():
    assert AgentDB.model_validate({"name": "Test Agent"}).model_dump() == {
        'id': AgentDB.id.default_factory(),
        'name': 'Test Agent',
        'role': 'worker',
        'system_prompt': '',
        'llm_provider': '',
        'llm_model': '',
        'status': 'idle',
        'created_at': AgentDB.created_at.default_factory(),
    }
    assert AgentDB.__tablename__ == "agents"
    assert AgentDB.id.primary_key is True
    assert AgentDB.id.default_factory is not None
    assert AgentDB.created_at.default_factory is not None


def test_task_db_model():
    assert TaskDB.model_validate({"description": "Test Task"}).model_dump() == {
        'id': TaskDB.id.default_factory(),
        'description': 'Test Task',
        'status': 'pending',
        'assigned_agents': [],
        'current_revision': 0,
        'max_revisions': 3,
        'final_output': '',
        'requires_human_approval': False,
        'created_at': TaskDB.created_at.default_factory(),
        'updated_at': TaskDB.updated_at.default_factory(),
        'parent_task_id': '',
        'depth': 0,
        'child_task_ids': [],
        'spawned_by_agent': '',
    }
    assert TaskDB.__tablename__ == "tasks"
    assert TaskDB.id.primary_key is True
    assert TaskDB.id.default_factory is not None
    assert TaskDB.created_at.default_factory is not None
    assert TaskDB.updated_at.default_factory is not None
    assert isinstance(TaskDB.assigned_agents.sa_column.type, JSON)
    assert isinstance(TaskDB.child_task_ids.sa_column.type, JSON)


def test_worker_output_db_model():
    worker_output_data = {
        "task_id": str(uuid.uuid4()),
        "agent_id": str(uuid.uuid4()),
        "agent_name": "Worker 1",
        "output": "Some output",
        "revision": 1,
    }
    assert WorkerOutputDB.model_validate(worker_output_data).model_dump() == {
        'id': None,
        'task_id': worker_output_data['task_id'],
        'agent_id': worker_output_data['agent_id'],
        'agent_name': worker_output_data['agent_name'],
        'output': worker_output_data['output'],
        'revision': worker_output_data['revision'],
        'timestamp': WorkerOutputDB.timestamp.default_factory(),
    }
    assert WorkerOutputDB.__tablename__ == "worker_outputs"
    assert WorkerOutputDB.id.primary_key is True
    assert WorkerOutputDB.task_id.foreign_key == "tasks.id"
    assert WorkerOutputDB.timestamp.default_factory is not None


def test_supervisor_review_db_model():
    supervisor_review_data = {
        "task_id": str(uuid.uuid4()),
        "decision": "approve",
        "feedback": "Looks good",
        "revision": 1,
    }
    assert SupervisorReviewDB.model_validate(supervisor_review_data).model_dump() == {
        'id': None,
        'task_id': supervisor_review_data['task_id'],
        'decision': supervisor_review_data['decision'],
        'feedback': supervisor_review_data['feedback'],
        'revision': supervisor_review_data['revision'],
        'timestamp': SupervisorReviewDB.timestamp.default_factory(),
    }
    assert SupervisorReviewDB.__tablename__ == "supervisor_reviews"
    assert SupervisorReviewDB.id.primary_key is True
    assert SupervisorReviewDB.task_id.foreign_key == "tasks.id"
    assert SupervisorReviewDB.timestamp.default_factory is not None


def test_execution_log_db_model():
    execution_log_data = {
        "task_id": str(uuid.uuid4()),
        "agent_id": str(uuid.uuid4()),
        "event_type": "tool_code",
        "message": "print('hello')",
        "extra_data": {"tool": "print"},
    }
    assert ExecutionLogDB.model_validate(execution_log_data).model_dump() == {
        'id': None,
        'task_id': execution_log_data['task_id'],
        'agent_id': execution_log_data['agent_id'],
        'event_type': execution_log_data['event_type'],
        'message': execution_log_data['message'],
        'extra_data': execution_log_data['extra_data'],
        'timestamp': ExecutionLogDB.timestamp.default_factory(),
    }
    assert ExecutionLogDB.__tablename__ == "execution_logs"
    assert ExecutionLogDB.id.primary_key is True
    assert ExecutionLogDB.timestamp.default_factory is not None
    assert isinstance(ExecutionLogDB.extra_data.sa_column.type, JSON)
