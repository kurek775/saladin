import asyncio
import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.models.schemas import WSEvent

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)
        logger.info("WebSocket client connected. Total: %d", len(self._connections))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)
        logger.info("WebSocket client disconnected. Total: %d", len(self._connections))

    async def broadcast(self, event: WSEvent) -> None:
        payload = event.model_dump_json()
        async with self._lock:
            stale: list[WebSocket] = []
            for ws in self._connections:
                try:
                    await ws.send_text(payload)
                except (RuntimeError, ConnectionError, OSError):
                    stale.append(ws)
            if stale:
                self._connections -= set(stale)

    @property
    def active_count(self) -> int:
        return len(self._connections)


ws_manager = ConnectionManager()
