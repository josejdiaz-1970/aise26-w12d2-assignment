from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: Exception,   
) -> JSONResponse:
    assert isinstance(exc, AppException)

    logger.warning(
        {
            "error_code": exc.code,
            "message": exc.message,
            "request_id": getattr(request.state, "request_id", None),
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        {
            "error": "UNHANDLED_EXCEPTION",
            "request_id": getattr(request.state, "request_id", None),
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )