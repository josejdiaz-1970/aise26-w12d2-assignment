import time
import logging
from fastapi import FastAPI, Request
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.request_id import RequestIDMiddleware
from app.api.v1.routes import health
from app.db.session import engine
from app.db import models
from app.api.v1.routes import items, auth
from app.core.redis_client import init_redis, close_redis
from contextlib import asynccontextmanager
from app.core.rate_limit import RateLimitMiddleware

# For exception handling
from app.core.exceptions import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    unhandled_exception_handler,
)

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware RequestID
app.add_middleware(RequestIDMiddleware)

#Middleware Rate Limit
app.add_middleware(RateLimitMiddleware)

# API versioning
app.include_router(health.router, prefix="/v1")

#Middleware logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": getattr(request.state, "request_id", None),
        }
    )

    return response

# Including routes for items
app.include_router(items.router, prefix="/v1")

# Including routes for authenitication
app.include_router(auth.router, prefix="/v1")

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

