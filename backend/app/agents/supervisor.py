import json
import logging
import re # Import re
from pydantic import ValidationError # Import ValidationError

from langchain_core.messages import HumanMessage

from app.agents.llm_factory import create_llm
from app.agents.prompts import SUPERVISOR_SYSTEM_PROMPT
from app.agents.state import SaladinState, ReviewResult # ReviewResult is now a Pydantic model

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
    """Extract and validate JSON decision from supervisor response."""
    # Regex to find a JSON block, optionally enclosed in ```json or ```
    json_match = re.search(r"```json\n({.*?})\n```", content, re.DOTALL)
    if not json_match:
        json_match = re.search(r"```\n({.*?})\n```", content, re.DOTALL)
    if not json_match:
        # Fallback to finding the first and last curly braces
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == -1 or start >= end:
            logger.warning("Failed to find JSON in supervisor response.")
            return ReviewResult(decision="revise", feedback="Could not parse supervisor response; requesting revision for safety")
        json_str = content[start:end]
    else:
        json_str = json_match.group(1)

    try:
        data = json.loads(json_str)
        # Use Pydantic for validation
        return ReviewResult(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("Failed to parse or validate supervisor decision: %s. Content: %s", e, content)
        return ReviewResult(decision="revise", feedback=f"Could not parse or validate supervisor response: {e}; requesting revision for safety")
