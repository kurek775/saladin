import logging

from langgraph.prebuilt import create_react_agent

from app.agents.llm_factory import create_llm
from app.agents.prompts import WORKER_SYSTEM_PROMPT
from app.agents.tools import search_memory, store_memory, summarize_text
from app.agents.tools_code import read_file, write_file, list_files, search_code, run_command
from app.agents.tools_tasks import create_task
from app.agents.tools_improvements import append_improvement_note
from app.config import settings

logger = logging.getLogger(__name__)

# Create a tool registry to map tool names to tool objects
TOOL_REGISTRY = {
    "search_memory": search_memory,
    "store_memory": store_memory,
    "summarize_text": summarize_text,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "search_code": search_code,
    "run_command": run_command,
    "create_task": create_task,
    "append_improvement_note": append_improvement_note,
}


def create_worker_agent(
    agent_id: str,
    custom_prompt: str = "",
    revision: int = 0,
    revision_feedback: str = "",
    llm_provider: str = "",
    llm_model: str = "",
    tools: list | None = None,
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

    # Use provided tools or dynamically load default tools from config
    if tools is None:
        # Retrieve tool objects from the registry based on names in settings
        default_tools = []
        for tool_name in settings.DEFAULT_WORKER_TOOL_NAMES:
            if tool_name in TOOL_REGISTRY:
                default_tools.append(TOOL_REGISTRY[tool_name])
            else:
                logger.warning(f"Tool '{tool_name}' not found in TOOL_REGISTRY.")
        tools = default_tools

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )

    return agent
