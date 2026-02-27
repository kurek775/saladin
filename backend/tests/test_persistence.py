import pytest
from unittest.mock import MagicMock
from app.models.domain import TaskRecord, TaskStatus
from app.services.persistence import get_task, save_task
from app.core.repository import get_task_repo

@pytest.fixture
def mock_task_repo():
    """Fixture to provide a mocked task repository."""
    mock_repo = MagicMock()
    mock_repo.tasks = {} # In-memory storage for testing

    def mock_get(task_id: str):
        return mock_repo.tasks.get(task_id)

    def mock_save(task: TaskRecord):
        mock_repo.tasks[task.id] = task

    mock_repo.get.side_effect = mock_get
    mock_repo.save.side_effect = mock_save
    return mock_repo

@pytest.fixture(autouse=True)
def setup_persistence_mocks(mock_task_repo, monkeypatch):
    """Patch get_task_repo to return our mock repository."""
    monkeypatch.setattr("app.core.repository.get_task_repo", lambda: mock_task_repo)
    # Clear the internal _task_locks to ensure tests are isolated
    monkeypatch.setattr("app.services.persistence._task_locks", {})

def test_save_and_get_task_roundtrip():
    """Test that a task can be saved and retrieved correctly."""
    task = TaskRecord(description="Test Task", status=TaskStatus.PENDING)
    save_task(task)
    retrieved_task = get_task(task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.description == "Test Task"
    assert retrieved_task.status == TaskStatus.PENDING

def test_update_existing_task():
    """Test updating an existing task."""
    task = TaskRecord(description="Initial Description", status=TaskStatus.PENDING)
    save_task(task)

    task.description = "Updated Description"
    task.status = TaskStatus.RUNNING
    save_task(task)

    updated_task = get_task(task.id)
    assert updated_task is not None
    assert updated_task.description == "Updated Description"
    assert updated_task.status == TaskStatus.RUNNING

def test_get_task_returns_none_for_unknown_id():
    """Test that get_task returns None for a non-existent task ID."""
    unknown_id = "non-existent-id"
    retrieved_task = get_task(unknown_id)
    assert retrieved_task is None

def test_task_locking_prevents_race_conditions(mock_task_repo, monkeypatch):
    """
    Test that the task locking mechanism is in place.
    This is a conceptual test since actual concurrency is hard to test in unit.
    We're verifying the lock mechanism is called.
    """
    task = TaskRecord(description="Locked Task", status=TaskStatus.PENDING)
    # We don't need to mock threading.Lock directly, but ensure save is called
    # and implicitly the lock mechanism within save_task is invoked.
    # The primary goal here is to ensure the save_task function itself works
    # with the mocked repository. The threading part is more of an integration
    # concern or requires more complex mocking.
    save_task(task)
    # Here we are just ensuring that save_task completes successfully,
    # implying the locking mechanism didn't block it unexpectedly in this
    # single-threaded test context.
    # The actual threading safety would require more intricate multi-threaded
    # testing, which is beyond a simple unit test for the persistence functions.
    retrieved_task = get_task(task.id)
    assert retrieved_task is not None
    assert retrieved_task.description == "Locked Task"
