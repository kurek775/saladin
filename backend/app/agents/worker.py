import logging

from langgraph.prebuilt import create_react_agent

from app.agents.llm_factory import create_llm
from app.agents.prompts import WORKER_SYSTEM_PROMPT
from app.agents.tools import search_memory, store_memory, summarize_text
from app.agents.tools_code import read_file, write_file, list_files, search_code, run_command
from app.agents.tools_tasks import create_task
from app.agents.tools_improvements import append_improvement_note

logger = logging.getLogger(__name__)


def create_worker_agent(
    agent_id: str,
    custom_prompt: str = "",
    revision: int = 0,
    revision_feedback: str = "",
    llm_provider: str = "",
    llm_model: str = "",
):
    """Create a ReAct worker agent with memory and summarization tools."""
    llm = create_llm(provider=llm_provider, model=llm_model, max_tokens=4096)

    feedback_text = ""
    if revision_feedback:
        feedback_text = f"Supervisor feedback from previous revision:\n{revision_feedback}"

    system_prompt = WORKER_SYSTEM_PROMPT.format(
        custom_prompt=custom_prompt or "No additional instructions.",
        revision=revision,
        revision_feedback=feedback_text,
    )

    tools = [
        search_memory, store_memory, summarize_text,
        read_file, write_file, list_files, search_code, run_command,
        create_task, append_improvement_note,
    ]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )

    return agent
