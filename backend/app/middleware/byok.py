"""BYOK middleware — extracts API keys from request headers into context vars."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.key_context import RequestKeys, request_keys


HEADER_MAP = {
    "x-openai-key": "openai",
    "x-anthropic-key": "anthropic",
    "x-google-key": "google",
}


class BYOKMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        keys = RequestKeys()
        for header, field in HEADER_MAP.items():
            value = request.headers.get(header, "")
            if value:
                setattr(keys, field, value)
        token = request_keys.set(keys)
        try:
            return await call_next(request)
        finally:
            request_keys.reset(token)
