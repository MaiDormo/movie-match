from typing import Any, Mapping
from fastapi.responses import JSONResponse


def create_response(
    status_code: int,
    message: str,
    data: Mapping[str, Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "status": "success" if status_code < 400 else "error",
        "message": message,
    }
    if data is not None:
        payload["data"] = dict(data)
    return JSONResponse(status_code=status_code, content=payload)


def create_error_response(
    status_code: int,
    message: str,
    data: Mapping[str, Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "status": "error",
        "message": message,
    }
    if data is not None:
        payload["data"] = dict(data)
    return JSONResponse(status_code=status_code, content=payload)