import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.event_bus import event_bus
from app.core.ws_manager import ws_manager
from app.core.log_filter import KeyScrubFilter
from app.middleware.byok import BYOKMiddleware
from app.api.routes import health, agents, tasks, settings as settings_routes, approval, scout
from app.api import websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Install key-scrubbing log filter on root logger
logging.getLogger().addFilter(KeyScrubFilter())


async def _broadcast_loop():
    """Consume events from the bus and broadcast to all WS clients."""
    consecutive_errors = 0
    while True:
        try:
            event = await event_bus.subscribe()
            await ws_manager.broadcast(event)
            consecutive_errors = 0  # Reset on success
        except Exception as e:
            consecutive_errors += 1
            logger.error("Broadcast error: %s (consecutive errors: %d)", e, consecutive_errors)
            if consecutive_errors >= settings.MAX_BROADCAST_ERROR_COUNT:
                logger.critical(
                    "Too many consecutive broadcast errors. Pausing for a longer period to prevent resource exhaustion."
                )
                await asyncio.sleep(settings.BROADCAST_ERROR_DELAY * 5)  # Longer pause
                consecutive_errors = 0 # Reset after long pause
            else:
                await asyncio.sleep(settings.BROADCAST_ERROR_DELAY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database if using postgres backend
    if settings.STORAGE_BACKEND == "postgres":
        from app.core.database import init_db
        init_db()

    # Pre-pull sandbox image to avoid cold-start latency
    pull_success = False
    for attempt in range(settings.SANDBOX_PULL_RETRIES):
        try:
            import docker
            client = docker.from_env()
            client.images.pull(settings.SANDBOX_IMAGE)
            logger.info("Pre-pulled sandbox image: %s", settings.SANDBOX_IMAGE)
            pull_success = True
            break
        except Exception as e:
            logger.warning(
                "Could not pre-pull sandbox image \'%s\' (attempt %d/%d): %s",
                settings.SANDBOX_IMAGE,
                attempt + 1,
                settings.SANDBOX_PULL_RETRIES,
                e,
            )
            if attempt < settings.SANDBOX_PULL_RETRIES - 1:
                await asyncio.sleep(settings.SANDBOX_PULL_RETRY_DELAY)
    
    if not pull_success:
        logger.error(
            "Failed to pre-pull sandbox image \'%s\' after %d attempts. This may lead to cold-start latency.",
            settings.SANDBOX_IMAGE,
            settings.SANDBOX_PULL_RETRIES,
        )

    # Start the broadcast consumer
    broadcast_task = asyncio.create_task(_broadcast_loop())
    logger.info("Saladin backend started (storage=%s)", settings.STORAGE_BACKEND)
    yield
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        logger.debug("Broadcast task was cancelled as expected.")
    logger.info("Saladin backend stopped")


app = FastAPI(title="Saladin", version="0.2.0", lifespan=lifespan)

# CORS — include BYOK headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-OpenAI-Key", "X-Anthropic-Key", "X-Google-Key"],
)

# BYOK middleware — extracts API keys from headers into context vars
app.add_middleware(BYOKMiddleware)

# Routers
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(settings_routes.router)
app.include_router(approval.router)
app.include_router(scout.router)
app.include_router(websocket.router)
