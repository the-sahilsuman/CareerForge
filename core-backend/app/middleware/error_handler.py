import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.errors import AppError


logger = logging.getLogger(__name__)


async def app_error_handler(
    request: Request,
    exc: AppError,
):
    request_id = request.headers.get("X-Request-ID")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
            }
        },
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    request_id = request.headers.get("X-Request-ID")

    logger.exception(
        "Unhandled application exception",
        extra={
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        },
    )