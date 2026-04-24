from fastapi import APIRouter
from controllers.vibe_service import get_all_vibes, get_movie_by_vibe
from pydantic import BaseModel
from typing import Dict, Any 

router = APIRouter()

# Response Model

class VibeResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

router.add_api_route(
        path="/api/v1/vibes",
        endpoint=get_all_vibes,
        response_model=VibeResponse,
        summary="Get Vibe list",
        description="List containing all of the available vibes",
        methods=["GET"]
)

router.add_api_route(
        "/api/v1/vibe/movies",
        endpoint=get_movie_by_vibe,
        response_model=VibeResponse,
        summary="Get movie by vibe",
        description= "Return 3 movies based on vibes",
        methods=["GET"]
)
