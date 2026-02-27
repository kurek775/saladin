
import pytest
from backend.app.agents.prompts import WORKER_SYSTEM_PROMPT, SUPERVISOR_SYSTEM_PROMPT

def test_worker_system_prompt_structure():
    """Test that the worker system prompt contains key elements and placeholders."""
    assert "You are a skilled worker agent" in WORKER_SYSTEM_PROMPT
    assert "{custom_prompt}" in WORKER_SYSTEM_PROMPT
    assert "Think through the task carefully" in WORKER_SYSTEM_PROMPT
    assert "Use any available tools if needed" in WORKER_SYSTEM_PROMPT
    assert "If you receive revision feedback from the supervisor" in WORKER_SYSTEM_PROMPT
    assert "Use `append_improvement_note`" in WORKER_SYSTEM_PROMPT
    assert "Use `create_task`" in WORKER_SYSTEM_PROMPT
    assert "Current task revision: {revision}" in WORKER_SYSTEM_PROMPT
    assert "{revision_feedback}" in WORKER_SYSTEM_PROMPT

def test_worker_system_prompt_formatting():
    """Test that the worker system prompt can be formatted correctly."""
    custom_p = "Do something specific."
    revision_num = 5
    feedback = "Please make it better."
    
    formatted_prompt = WORKER_SYSTEM_PROMPT.format(
        custom_prompt=custom_p,
        revision=revision_num,
        revision_feedback=feedback
    )
    
    assert custom_p in formatted_prompt
    assert f"Current task revision: {revision_num}" in formatted_prompt
    assert feedback in formatted_prompt
    assert "{custom_prompt}" not in formatted_prompt # Ensure all placeholders are replaced
    assert "{revision}" not in formatted_prompt
    assert "{revision_feedback}" not in formatted_prompt

def test_supervisor_system_prompt_structure():
    """Test that the supervisor system prompt contains key elements and placeholders."""
    assert "You are the Supervisor agent" in SUPERVISOR_SYSTEM_PROMPT
    assert "respond with a JSON decision" in SUPERVISOR_SYSTEM_PROMPT
    assert """{{
  "decision": "approve" | "reject" | "revise",
  "feedback": "Your detailed feedback here"
}}""" in SUPERVISOR_SYSTEM_PROMPT # Check for the JSON structure
    assert "Guidelines:" in SUPERVISOR_SYSTEM_PROMPT
    assert "- **approve**" in SUPERVISOR_SYSTEM_PROMPT
    assert "- **revise**" in SUPERVISOR_SYSTEM_PROMPT
    assert "- **reject**" in SUPERVISOR_SYSTEM_PROMPT
    assert "Current revision: {revision} of {max_revisions}" in SUPERVISOR_SYSTEM_PROMPT
    assert "Task description: {task_description}" in SUPERVISOR_SYSTEM_PROMPT
    assert "Worker outputs to review:" in SUPERVISOR_SYSTEM_PROMPT
    assert "{worker_outputs}" in SUPERVISOR_SYSTEM_PROMPT

def test_supervisor_system_prompt_formatting():
    """Test that the supervisor system prompt can be formatted correctly."""
    revision_num = 2
    max_revs = 3
    task_desc = "Implement feature X."
    worker_out = "Worker A output: ..."
    
    formatted_prompt = SUPERVISOR_SYSTEM_PROMPT.format(
        revision=revision_num,
        max_revisions=max_revs,
        task_description=task_desc,
        worker_outputs=worker_out
    )
    
    assert f"Current revision: {revision_num} of {max_revs}" in formatted_prompt
    assert f"Task description: {task_desc}" in formatted_prompt
    assert f"Worker outputs to review:\n{worker_out}" in formatted_prompt
    assert "{revision}" not in formatted_prompt
    assert "{max_revisions}" not in formatted_prompt
    assert "{task_description}" not in formatted_prompt
    assert "{worker_outputs}" not in formatted_prompt
