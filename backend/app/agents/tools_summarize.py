"""Summarization tool — compresses long text using a fast/cheap LLM."""

import logging

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

DEFAULT_MAX_LENGTH = 3000  # characters threshold


@tool
def summarize_text(text: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Summarize long text into a concise version while preserving key information.

    Args:
        text: The text to summarize.
        max_length: Maximum character length threshold. Text shorter than this is returned as-is.
    """
    if len(text) <= max_length:
        return text

    try:
        from app.agents.llm_factory import create_llm
        # Use a fast/cheap model for summarization
        llm = create_llm(max_tokens=1024)
        prompt = (
            "Summarize the following text concisely while preserving all key information, "
            "facts, and conclusions. Keep the summary under 2000 characters.\n\n"
            f"Text:\n{text[:8000]}"
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return str(response.content)
    except Exception as e:
        logger.warning("Summarization failed, using truncation: %s", e)
        return text[:max_length] + "\n[... truncated ...]"
