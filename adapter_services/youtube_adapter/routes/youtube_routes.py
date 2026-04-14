from fastapi import APIRouter
from controllers.youtube_controller import search_youtube
from pydantic import BaseModel, Field
from typing import Any

router = APIRouter()


class YoutubeResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: dict[str, str] = Field(..., description="YouTube video details including ID and embed URL")


SUCCESS_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "YouTube video successfully retrieved!",
    "data": {
        "video_id": "kVrqfYjkTdQ",
        "embed_url": "https://www.youtube.com/embed/kVrqfYjkTdQ",
    },
}

ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    401: {"status": "error", "message": "Invalid YouTube API credentials"},
    404: {"status": "error", "message": "No videos found for the provided query"},
    405: {"status": "error", "message": "Method not allowed"},
    422: {
        "status": "error",
        "code": 422,
        "message": "Request validation failed",
        "details": [
            {
                "field": "query -> query",
                "message": "field required",
                "type": "missing",
            }
        ],
    },
    429: {"status": "error", "message": "YouTube API quota exceeded. Please try again later."},
    500: {"status": "error", "message": "Failed to fetch video from YouTube API"},
    503: {"status": "error", "message": "YouTube service is currently unavailable"},
    504: {"status": "error", "message": "Request to YouTube API timed out"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Video found successfully",
    401: "Invalid YouTube API credentials",
    404: "No videos found",
    405: "Method not allowed",
    422: "Validation error",
    429: "YouTube API quota exceeded",
    500: "Internal server error",
    503: "YouTube service unavailable",
    504: "Gateway timeout",
}

ROUTE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Video found",
                        "value": SUCCESS_EXAMPLE,
                    }
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    ROUTE_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }


router.get(
    "/api/v1/get_video",
    response_model=YoutubeResponse,
    summary="Get YouTube Video",
    description="Search for a video on YouTube and get its embed URL",
    responses=ROUTE_RESPONSES,
)(search_youtube)