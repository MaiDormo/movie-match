from fastapi import APIRouter
from controllers.youtube_controller import health_check, search_youtube
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class YoutubeResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Dict[str, str] = Field(..., description="YouTube video details including ID and embed URL")
class ValidationError(BaseModel):
    field: str = Field(..., description="Path to the field that failed validation")
    message: str = Field(..., description="Description of the validation error")
    type: str = Field(..., description="Type of validation error")

class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the YouTube API adapter service is running",
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
                                "message": "YouTube API adapter is up and running"
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
    "/api/v1/get_video",
    response_model=YoutubeResponse,
    summary="Get YouTube Video",
    description="Search for a video on YouTube and get its embed URL",
    responses={
        200: {
            "description": "Video found successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Video found",
                            "value": {
                                "status": "success",
                                "message": "YouTube video successfully retrieved!",
                                "data": {
                                    "video_id": "kVrqfYjkTdQ",
                                    "embed_url": "https://www.youtube.com/embed/kVrqfYjkTdQ"
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid YouTube API credentials",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid YouTube API credentials"
                    }
                }
            }
        },
        404: {
            "description": "No videos found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "No videos found for the provided query"
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
                        "message": "Method not allowed"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> query",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "YouTube API quota exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "YouTube API quota exceeded. Please try again later."
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
                        "message": "Failed to fetch video from YouTube API"
                    }
                }
            }
        },
        503: {
            "description": "YouTube service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "YouTube service is currently unavailable"
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
                        "message": "Request to YouTube API timed out"
                    }
                }
            }
        }
    }
)(search_youtube)