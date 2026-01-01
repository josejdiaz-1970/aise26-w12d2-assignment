from redis.asyncio.client import Redis as AsyncRedis
from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import engine
from app.core.redis_client import init_redis

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/detailed")
async def health_detailed():
    checks: dict[str, str] = {}

    # Database check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "down"

    # Redis check
    try:
        redis: AsyncRedis = await init_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "down"

    return {
        "status": "ok" if all(v == "ok" for v in checks.values()) else "degraded",
        "checks": checks,
    }