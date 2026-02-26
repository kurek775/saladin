"""Tests for the graph structure (no LLM calls)."""
from app.agents.state import SaladinState, ReviewResult
from app.agents.graph import should_continue


def test_should_continue_approve():
    state: SaladinState = {
        "task_id": "t1",
        "task_description": "test",
        "assigned_agent_ids": [],
        "messages": [],
        "worker_outputs": [],
        "supervisor_review": ReviewResult(decision="approve", feedback="good"),
        "current_revision": 0,
        "max_revisions": 3,
        "final_output": "",
        "status": "under_review",
    }
    assert should_continue(state) == "approve"


def test_should_continue_revise():
    state: SaladinState = {
        "task_id": "t1",
        "task_description": "test",
        "assigned_agent_ids": [],
        "messages": [],
        "worker_outputs": [],
        "supervisor_review": ReviewResult(decision="revise", feedback="needs work"),
        "current_revision": 1,
        "max_revisions": 3,
        "final_output": "",
        "status": "under_review",
    }
    assert should_continue(state) == "revise"


def test_should_continue_max_revisions():
    state: SaladinState = {
        "task_id": "t1",
        "task_description": "test",
        "assigned_agent_ids": [],
        "messages": [],
        "worker_outputs": [],
        "supervisor_review": ReviewResult(decision="revise", feedback="needs work"),
        "current_revision": 3,
        "max_revisions": 3,
        "final_output": "",
        "status": "under_review",
    }
    # Should auto-approve at max revisions
    assert should_continue(state) == "approve"


def test_should_continue_reject():
    state: SaladinState = {
        "task_id": "t1",
        "task_description": "test",
        "assigned_agent_ids": [],
        "messages": [],
        "worker_outputs": [],
        "supervisor_review": ReviewResult(decision="reject", feedback="bad"),
        "current_revision": 0,
        "max_revisions": 3,
        "final_output": "",
        "status": "under_review",
    }
    assert should_continue(state) == "reject"
