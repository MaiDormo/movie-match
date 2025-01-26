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

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Spotify API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Service healthy",
                            "value": {
                                "status": "success",
                                "message": "Spotify API adapter is up and running"
                            }
                        }
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The HTTP method is not allowed for this endpoint"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        }
    }
)(health_check)

router.get(
    "/api/v1/search_playlist",
    response_model=PlaylistResponse,
    summary="Search Playlist",
    description="Search for a playlist on Spotify and get its details",
    responses={
        200: {
            "description": "Playlist found successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Playlist found",
                            "value": {
                                "status": "success",
                                "message": "Playlist found successfully",
                                "data": {
                                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX7g9DBqVEIX",
                                    "cover_url": "https://i.scdn.co/image/ab67706c0000da84c5e8f3742242066438d9e74",
                                    "name": "Titanic (Original Motion Picture Soundtrack)"
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid Spotify API credentials",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid Spotify API credentials"
                    }
                }
            }
        },
        404: {
            "description": "No playlist found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "No playlist found for the given search criteria"
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The HTTP method is not allowed for this endpoint"
                    }
                }
            }
        },
        422: {
            "description": "Request validation failed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> movie_title",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "Spotify API rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Spotify API rate limit exceeded. Please try again later."
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error or incomplete playlist data"
                    }
                }
            }
        },
        503: {
            "description": "Spotify service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Spotify service is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Gateway timeout",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to Spotify API timed out"
                    }
                }
            }
        }
    }
)(get_playlist_info)