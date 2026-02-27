
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services import evaluation
from app.models.domain import Task, WorkerOutput
from datetime import datetime

@pytest.fixture
def mock_get_task():
    with patch('app.services.task_service.get_task') as mock_get_task_func:
        yield mock_get_task_func

@pytest.fixture
def sample_task():
    return Task(
        id="task123",
        description="What is the capital of France?",
        final_output="Paris",
        worker_outputs=[
            WorkerOutput(agent_id="agent1", output="The capital of France is Paris.", timestamp=datetime.now())
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.mark.asyncio
async def test_evaluate_task_not_found(mock_get_task):
    mock_get_task.return_value = None
    result = await evaluation.evaluate_task("nonexistent_task")
    assert result is None
    mock_get_task.assert_called_once_with("nonexistent_task")

@pytest.mark.asyncio
async def test_evaluate_task_no_final_output(mock_get_task, sample_task):
    sample_task.final_output = ""
    mock_get_task.return_value = sample_task
    result = await evaluation.evaluate_task(sample_task.id)
    assert result is None
    mock_get_task.assert_called_once_with(sample_task.id)

@pytest.mark.asyncio
async def test_evaluate_task_ragas_not_installed(mock_get_task, sample_task):
    mock_get_task.return_value = sample_task
    with patch.dict('sys.modules', {'ragas': None, 'ragas.metrics': None, 'datasets': None}):
        result = await evaluation.evaluate_task(sample_task.id)
        assert result is None
    mock_get_task.assert_called_once_with(sample_task.id)

@pytest.mark.asyncio
async def test_evaluate_task_ragas_exception(mock_get_task, sample_task):
    mock_get_task.return_value = sample_task
    with patch('ragas.evaluate', side_effect=Exception("RAGAS error")):
        with patch('datasets.Dataset.from_dict', return_value=MagicMock()):
            result = await evaluation.evaluate_task(sample_task.id)
            assert result is None
    mock_get_task.assert_called_once_with(sample_task.id)

@pytest.mark.asyncio
async def test_evaluate_task_success(mock_get_task, sample_task):
    mock_get_task.return_value = sample_task
    
    mock_ragas_evaluate_result = MagicMock()
    mock_ragas_evaluate_result.get.side_effect = lambda key, default: {
        "faithfulness": 0.9,
        "answer_relevancy": 0.8,
    }.get(key, default)

    with patch('ragas.evaluate', return_value=mock_ragas_evaluate_result) as mock_evaluate,
         patch('datasets.Dataset.from_dict', return_value=MagicMock()) as mock_from_dict:
        
        result = await evaluation.evaluate_task(sample_task.id)
        
        mock_get_task.assert_called_once_with(sample_task.id)
        mock_from_dict.assert_called_once()
        assert mock_from_dict.call_args[0][0]["question"] == [sample_task.description]
        assert mock_from_dict.call_args[0][0]["answer"] == [sample_task.final_output]
        assert mock_from_dict.call_args[0][0]["contexts"] == [[wo.output for wo in sample_task.worker_outputs]]

        mock_evaluate.assert_called_once()
        assert result == {"task_id": sample_task.id, "faithfulness": 0.9, "answer_relevancy": 0.8}
