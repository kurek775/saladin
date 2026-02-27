"""Task/agent context for tools — tells tools which task/agent they're inside.

Same pattern as key_context.py: a ContextVar that propagates through asyncio.gather().
"""

import contextvars
from dataclasses import dataclass


@dataclass
class ToolContext:
    task_id: str = ""
    agent_id: str = ""


_tool_context: contextvars.ContextVar[ToolContext] = contextvars.ContextVar(
    "_tool_context", default=ToolContext()
)


def get_tool_context() -> ToolContext:
    return _tool_context.get()


def set_tool_context(ctx: ToolContext) -> contextvars.Token:
    return _tool_context.set(ctx)


def reset_tool_context(token: contextvars.Token) -> None:
    _tool_context.reset(token)
