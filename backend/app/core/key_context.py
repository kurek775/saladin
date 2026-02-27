"""Request-scoped BYOK key context using contextvars.

Keys set here propagate correctly through asyncio.gather() in worker dispatch.
"""

import contextvars
from dataclasses import dataclass


@dataclass
class RequestKeys:
    openai: str = ""
    anthropic: str = ""
    google: str = ""


request_keys: contextvars.ContextVar[RequestKeys] = contextvars.ContextVar(
    "request_keys", default=RequestKeys()
)


def get_request_keys() -> RequestKeys:
    return request_keys.get()
