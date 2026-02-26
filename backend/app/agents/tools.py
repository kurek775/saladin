from langchain_core.tools import tool


@tool
def search_memory(query: str, agent_id: str = "") -> str:
    """Search the agent's memory for relevant information.

    Args:
        query: The search query to find relevant memories.
        agent_id: The agent ID whose memory to search.
    """
    from app.services.memory_service import search_memories
    results = search_memories(agent_id, query)
    if not results:
        return "No relevant memories found."
    return "\n\n".join(results)


@tool
def store_memory(content: str, agent_id: str = "") -> str:
    """Store information in the agent's long-term memory.

    Args:
        content: The information to store in memory.
        agent_id: The agent ID whose memory to store in.
    """
    from app.services.memory_service import store_memory_entry
    store_memory_entry(agent_id, content)
    return "Memory stored successfully."
