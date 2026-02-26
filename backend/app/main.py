import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.event_bus import event_bus
from app.core.ws_manager import ws_manager
from app.api.routes import health, agents, tasks
from app.api import websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _broadcast_loop():
    """Consume events from the bus and broadcast to all WS clients."""
    while True:
        event = await event_bus.subscribe()
        try:
            await ws_manager.broadcast(event)
        except Exception as e:
            logger.error("Broadcast error: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the broadcast consumer
    broadcast_task = asyncio.create_task(_broadcast_loop())
    logger.info("Saladin backend started")
    yield
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass
    logger.info("Saladin backend stopped")


app = FastAPI(title="Saladin", version="0.1.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(websocket.router)
