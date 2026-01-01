import redis.asyncio as redis_async
from app.core.config import settings

_redis: redis_async.Redis | None = None


async def init_redis() -> redis_async.Redis:
    global _redis
    if _redis is None:
        _redis = redis_async.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )    
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None