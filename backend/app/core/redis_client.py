"""Redis connection management."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)

_redis = None
_arq_pool = None


async def get_redis():
    """Get an async Redis connection."""
    global _redis
    if _redis is None:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def get_arq_pool():
    """Get an ARQ connection pool for job enqueueing."""
    global _arq_pool
    if _arq_pool is None:
        from arq import create_pool
        from arq.connections import RedisSettings
        # Parse redis URL
        _arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return _arq_pool


async def close_redis():
    """Close Redis connections."""
    global _redis, _arq_pool
    if _redis:
        await _redis.close()
        _redis = None
    if _arq_pool:
        await _arq_pool.close()
        _arq_pool = None
