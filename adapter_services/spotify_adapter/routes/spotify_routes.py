from fastapi import APIRouter
from controllers.spotify_controller import get_playlist_info
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models

class SpotifyResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Playlist details from Spotify")


SUCCESS_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Youtube video successfully retrieved!",
    "data": {
        "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX7g9DBqVEIX",
        "cover_url": "https://i.scdn.co/image/ab67706c0000da84c5e8f3742242066438d9e74",
        "name": "Titanic (Original Motion Picture Soundtrack)"
    }
}

ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    401: {"status": "error", "message": "Invalid Spotify API credentials"},
    404: {"status": "error", "message": "No playlist found"},
    405: {"status": "error", "message": "Method not allowed"},
    422: {
        "status": "error",
        "code": 422,
        "message": "Request validation failed",
        "details": [
            {
                "field": "query -> movie_title",
                "message": "field required",
                "type": "missing"
            }
        ],
    },
    429: {"status": "error", "message": "Spotify API rate limit exceeded"},
    500: {"status": "error", "message": "Failed to fetch playlist from Spotify API"},
    503: {"status": "error", "message": "Spotify service is currently unavailable"},
    504: {"status": "error", "message": "Request to Spotify API timed out"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Playlist found successfully",
    401: "Invalid Spotify API credentials",
    404: "No playlist found",
    405: "Method not allowed",
    422: "Validation error",
    429: "Spotify API quota exceeded",
    500: "Internal server error",
    503: "Spotify service unavailable",
    504: "Gateway timeout",
}

ROUTE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Playlist found",
                        "value": SUCCESS_EXAMPLE
                    }
                }
            }
        }
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    ROUTE_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }


router.get(
    "/api/v1/search_playlist",
    response_model=SpotifyResponse,
    summary="Search Playlist",
    description="Search for a playlist on Spotify and get its details",
    responses=ROUTE_RESPONSES
)(get_playlist_info)