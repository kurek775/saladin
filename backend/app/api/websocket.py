import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.core.ws_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            try:
                # Wait for client message with heartbeat timeout
                await asyncio.wait_for(
                    ws.receive_text(),
                    timeout=settings.WS_HEARTBEAT_INTERVAL,
                )
            except asyncio.TimeoutError:
                # Send ping to check if client is alive
                try:
                    await ws.send_json({"type": "ping"})
                except Exception as e:
                    logger.warning(f"Failed to send ping or client disconnected: {e}")
                    break
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {ws.client}")
    except Exception as e:
        logger.error(f"WebSocket error for client {ws.client}: {e}", exc_info=True)
    finally:
        await ws_manager.disconnect(ws)
