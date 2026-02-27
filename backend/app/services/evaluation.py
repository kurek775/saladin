"""RAGAS evaluation service — scores completed tasks on Faithfulness and Answer Relevance."""

import logging

logger = logging.getLogger(__name__)


async def evaluate_task(task_id: str) -> dict | None:
    """Evaluate a completed task using RAGAS metrics.

    Scores: Faithfulness (how factually consistent) and Answer Relevance.
    Returns dict with scores or None if evaluation not possible.

    This is opt-in per task as it incurs extra LLM cost.
    """
    from app.services.task_service import get_task

    task = get_task(task_id)
    if task is None:
        logger.error("Task %s not found for evaluation", task_id)
        return None

    if not task.final_output:
        logger.warning("Task %s has no final output to evaluate", task_id)
        return None

    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from datasets import Dataset

        # Build evaluation dataset
        data = {
            "question": [task.description],
            "answer": [task.final_output],
            "contexts": [[wo.output for wo in task.worker_outputs]],
        }
        dataset = Dataset.from_dict(data)

        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy],
        )

        scores = {
            "task_id": task_id,
            "faithfulness": result.get("faithfulness", None),
            "answer_relevancy": result.get("answer_relevancy", None),
        }
        logger.info("RAGAS evaluation for task %s: %s", task_id, scores)
        return scores

    except ImportError:
        logger.warning("RAGAS not installed, skipping evaluation")
        return None
    except Exception as e:
        logger.error("RAGAS evaluation failed for task %s: %s", task_id, e)
        return None
