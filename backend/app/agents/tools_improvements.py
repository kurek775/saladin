"""Tool: append_improvement_note — logs structured observations to IMPROVEMENTS.md."""

import logging
from datetime import datetime, UTC
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def append_improvement_note(
    category: str,
    observation: str,
    suggested_action: str,
    priority: str = "medium",
) -> str:
    """Append a structured improvement observation to IMPROVEMENTS.md.

    Use this when you notice issues, patterns, or opportunities outside your current task scope.

    Args:
        category: Category of the improvement (e.g., "code-quality", "performance", "security", "architecture", "testing").
        observation: What you observed that needs attention.
        suggested_action: What should be done to address it.
        priority: Priority level — "low", "medium", or "high".

    Returns:
        Confirmation message.
    """
    from app.agents._tool_context import get_tool_context
    from app.config import settings

    ctx = get_tool_context()

    workspace = Path(settings.WORKSPACE_DIR).resolve()
    improvements_path = workspace / "IMPROVEMENTS.md"

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    task_label = ctx.task_id[:8] if ctx.task_id else "unknown"
    agent_label = ctx.agent_id[:8] if ctx.agent_id else "unknown"

    entry = (
        f"\n### [{category.upper()}] {observation[:80]}\n"
        f"- **Priority:** {priority}\n"
        f"- **Observation:** {observation}\n"
        f"- **Suggested action:** {suggested_action}\n"
        f"- **Logged by:** task `{task_label}` / agent `{agent_label}` at {timestamp}\n"
    )

    try:
        if not improvements_path.exists():
            improvements_path.write_text(
                "# Saladin Self-Improvement Log\n\n"
                "Automatically generated observations from agent tasks.\n\n"
                "---\n"
            )

        with open(improvements_path, "a") as f:
            f.write(entry)

        logger.info("Improvement note appended: [%s] %s", category, observation[:60])
        return f"Logged improvement note under [{category.upper()}]."
    except Exception as e:
        logger.error("Failed to write improvement note: %s", e)
        return f"Error writing improvement note: {e}"
