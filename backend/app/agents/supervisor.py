import json
import logging

from langchain_core.messages import HumanMessage

from app.agents.llm_factory import create_llm
from app.agents.prompts import SUPERVISOR_SYSTEM_PROMPT
from app.agents.state import SaladinState, ReviewResult

logger = logging.getLogger(__name__)

MAX_OUTPUT_PER_WORKER = 4000
MAX_TOTAL_OUTPUT = 12000


def _smart_truncate(text: str, max_length: int) -> str:
    """Intelligently truncate or summarize text."""
    if len(text) <= max_length:
        return text

    try:
        from app.agents.tools_summarize import summarize_text
        return summarize_text.invoke({"text": text, "max_length": max_length})
    except Exception:
        return text[:max_length] + "\n[... truncated ...]"


async def supervisor_review(state: SaladinState, llm_provider: str = "", llm_model: str = "") -> dict:
    """Supervisor node: reviews worker outputs and returns a decision."""
    llm = create_llm(provider=llm_provider, model=llm_model, max_tokens=2048)

    # Format worker outputs for review with intelligent summarization
    output_parts = []
    for wo in state["worker_outputs"]:
        text = _smart_truncate(wo["output"], MAX_OUTPUT_PER_WORKER)
        output_parts.append(f"\n--- Worker: {wo['agent_name']} ---\n{text}")
    outputs_text = "\n".join(output_parts)
    if len(outputs_text) > MAX_TOTAL_OUTPUT:
        outputs_text = _smart_truncate(outputs_text, MAX_TOTAL_OUTPUT)

    revision = state.get("current_revision", 0)
    max_revisions = state.get("max_revisions", 3)

    prompt = SUPERVISOR_SYSTEM_PROMPT.format(
        revision=revision,
        max_revisions=max_revisions,
        task_description=state["task_description"],
        worker_outputs=outputs_text,
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    content = response.content

    decision = _parse_decision(content)

    return {
        "supervisor_review": decision,
        "messages": [response],
    }


def _parse_decision(content: str) -> ReviewResult:
    """Extract JSON decision from supervisor response."""
    try:
        text = content
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            decision = data.get("decision", "revise").lower()
            if decision not in ("approve", "reject", "revise"):
                decision = "revise"
            return ReviewResult(
                decision=decision,
                feedback=data.get("feedback", ""),
            )
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.warning("Failed to parse supervisor decision: %s", e)

    return ReviewResult(decision="revise", feedback="Could not parse supervisor response; requesting revision for safety")
