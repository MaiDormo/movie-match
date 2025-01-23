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

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "YouTube video successfully retrieved!",
                "data": {
                    "video_id": "kVrqfYjkTdQ",
                    "embed_url": "https://www.youtube.com/embed/kVrqfYjkTdQ"
                }
            }
        }

class ValidationError(BaseModel):
    field: str = Field(..., description="Path to the field that failed validation")
    message: str = Field(..., description="Description of the validation error")
    type: str = Field(..., description="Type of validation error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> query",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
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

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the YouTube API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "Method not allowed", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/get_video",
    response_model=YoutubeResponse,
    summary="Get YouTube Video",
    description="Search for a video on YouTube and get its embed URL",
    responses={
        200: {"description": "Video found successfully", "model": YoutubeResponse},
        401: {"description": "Invalid YouTube API credentials", "model": BaseResponse},
        404: {"description": "No videos found for the provided query", "model": BaseResponse},
        422: {"description": "Request validation failed (invalid query format)", "model": BaseResponse},
        429: {"description": "YouTube API quota exceeded", "model": BaseResponse},
        500: {"description": "Internal server error or failed to fetch video from YouTube API", "model": BaseResponse},
        503: {"description": "YouTube service is currently unavailable", "model": BaseResponse},
        504: {"description": "Request to YouTube API timed out", "model": BaseResponse}
    }
)(search_youtube)