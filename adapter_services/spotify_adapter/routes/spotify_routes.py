from fastapi import APIRouter
from controllers.spotify_controller import health_check, get_playlist_info
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class PlaylistResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="Playlist details from Spotify")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Playlist found successfully",
                "data": {
                    "spotify_url": "https://open.spotify.com/playlist/...",
                    "cover_url": "https://i.scdn.co/image/...",
                    "name": "Titanic Soundtrack"
                }
            }
        }

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> song_name",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "query -> song_name",
                        "message": "field required",
                        "type": "missing"
                    }
                ]
            }
        }

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Spotify API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/search_playlist",
    response_model=PlaylistResponse,
    summary="Search Playlist", 
    description="Search for a playlist on Spotify and get its details",
    responses={
        200: {"description": "Playlist found successfully", "model": PlaylistResponse},
        401: {"description": "Invalid Spotify API credentials", "model": BaseResponse},
        404: {"description": "No playlist found", "model": BaseResponse},
        422: {"description": "Request validation failed", "model": ErrorResponse},
        429: {"description": "Spotify API rate limit exceeded", "model": BaseResponse},
        500: {"description": "Internal server error or incomplete playlist data", "model": BaseResponse},
        503: {"description": "Spotify service is currently unavailable", "model": BaseResponse},
        504: {"description": "Request to Spotify API timed out", "model": BaseResponse}
    }
)(get_playlist_info)