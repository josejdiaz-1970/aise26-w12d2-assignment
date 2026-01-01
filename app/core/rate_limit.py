import time
from dataclasses import dataclass
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.redis_client import init_redis


@dataclass
class RateLimitResult:
    limit: int
    remaining: int
    reset: int  # unix seconds
    allowed: bool


def _client_key(request: Request) -> str:
    
    ip = request.client.host if request.client else "unknown"
    return ip


async def check_rate_limit(key: str, limit: int, window_seconds: int) -> RateLimitResult:
    r = await init_redis()
    now = int(time.time())
    window_start = now - window_seconds

    # Sliding window using a sorted set
    zkey = f"rl:{key}"
    pipe = r.pipeline()
    pipe.zremrangebyscore(zkey, 0, window_start)
    pipe.zadd(zkey, {str(now): now})
    pipe.zcard(zkey)
    pipe.expire(zkey, window_seconds + 5)
    _, _, count, _ = await pipe.execute()

    count = int(count)
    allowed = count <= limit
    remaining = max(0, limit - count)
    reset = now + window_seconds

    return RateLimitResult(limit=limit, remaining=remaining, reset=reset, allowed=allowed)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow public endpoints without rate limit if you want
        path = request.url.path
        if path.startswith("/v1/health") or path.startswith("/docs") or path.startswith("/openapi.json"):
            return await call_next(request)

        key = _client_key(request)
        result = await check_rate_limit(
            key=key,
            limit=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )

        if not result.allowed:
            retry_after = max(0, result.reset - int(time.time()))
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests",
                        "request_id": getattr(request.state, "request_id", None),
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(result.limit),
                    "X-RateLimit-Remaining": str(result.remaining),
                    "X-RateLimit-Reset": str(result.reset),
                },
            )

        response = await call_next(request)

        # Add rate limit headers on successful responses too
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset)
        return response