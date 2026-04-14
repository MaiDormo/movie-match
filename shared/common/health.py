# shared/common/health.py
from fastapi import APIRouter
from fastapi import status
from .response import create_response


def health_router(service_name: str, path: str = "/health") -> APIRouter:
    router = APIRouter(tags=["Health"])

    @router.get(path)
    async def health_check():
        return create_response(
            status_code=status.HTTP_200_OK,
            message=f"{service_name} is up and running!",
        )

    return router