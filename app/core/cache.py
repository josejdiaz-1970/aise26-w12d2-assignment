import hashlib
import json
from fastapi import Request
from app.core.config import settings
from app.core.redis_client import init_redis
from typing import Any


def _cache_key_from_request(request: Request, prefix: str) -> str:
    # include path + query params + (optionally) user identity
    raw = f"{request.url.path}?{request.url.query}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"cache:{prefix}:{digest}"


async def cache_get(request: Request, prefix: str) -> Any | None:
    r = await init_redis()
    key = _cache_key_from_request(request, prefix)
    val = await r.get(key)
    if val:
        return json.loads(val)
    return None


async def cache_set(request: Request, prefix: str, payload: Any) -> None:
    r = await init_redis()
    key = _cache_key_from_request(request, prefix)
    await r.setex(key, settings.cache_ttl_seconds, json.dumps(payload))


async def cache_invalidate_prefix(prefix: str) -> None:
    # Simple invalidation: delete all keys for prefix (fine for small projects)
    r = await init_redis()
    pattern = f"cache:{prefix}:*"
    async for k in r.scan_iter(match=pattern):
        await r.delete(k)