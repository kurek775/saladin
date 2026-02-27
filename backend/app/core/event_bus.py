import asyncio
import logging

from app.models.schemas import WSEvent

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self, maxsize: int = 1000) -> None:
        self._queue: asyncio.Queue[WSEvent] = asyncio.Queue(maxsize=maxsize)

    async def publish(self, event: WSEvent) -> None:
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            # Drop oldest event to make room
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                logger.debug("Attempted to drop event from an already empty queue.")
            self._queue.put_nowait(event)
            logger.warning("Event bus full, dropped oldest event")

    async def subscribe(self) -> WSEvent:
        return await self._queue.get()

    def empty(self) -> bool:
        return self._queue.empty()


event_bus = EventBus()
