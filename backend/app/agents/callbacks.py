import asyncio
import logging
from datetime import datetime, UTC
from typing import Any
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler

from app.models.schemas import WSEvent
from app.core.event_bus import event_bus

logger = logging.getLogger(__name__)


class SaladinCallbackHandler(AsyncCallbackHandler):
    """Bridges LangChain events to the WebSocket event bus."""

    def __init__(self, task_id: str, agent_id: str = "", agent_name: str = ""):
        self.task_id = task_id
        self.agent_id = agent_id
        self.agent_name = agent_name

    async def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs) -> None:
        await event_bus.publish(WSEvent(
            type="log",
            data={
                "task_id": self.task_id,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "level": "info",
                "message": f"LLM started for agent {self.agent_name or 'supervisor'}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))

    async def on_llm_end(self, response: Any, **kwargs) -> None:
        await event_bus.publish(WSEvent(
            type="log",
            data={
                "task_id": self.task_id,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "level": "info",
                "message": f"LLM completed for agent {self.agent_name or 'supervisor'}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))

    async def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "unknown")
        await event_bus.publish(WSEvent(
            type="log",
            data={
                "task_id": self.task_id,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "level": "info",
                "message": f"Tool '{tool_name}' invoked by {self.agent_name}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))

    async def on_llm_error(self, error: BaseException, **kwargs) -> None:
        await event_bus.publish(WSEvent(
            type="log",
            data={
                "task_id": self.task_id,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "level": "error",
                "message": f"LLM error: {error}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ))
