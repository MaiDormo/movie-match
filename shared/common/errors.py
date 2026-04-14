# shared/common/errors.py
from typing import Any
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _error_payload(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "error", "message": message}
    if data is not None:
        payload["data"] = data
    return payload


async def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("Internal server error"),
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload("Validation error", {"errors": exc.errors()}),
    )


async def http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    # FastAPI expects handlers typed against Exception; narrow at runtime.
    if not isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("Internal server error"),
        )

    # Preserve FastAPI status code behavior, standardize body shape.
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(str(exc.detail)),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    # Avoid leaking internals in production if needed.
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload("Internal server error", {"detail": str(exc)}),
    )