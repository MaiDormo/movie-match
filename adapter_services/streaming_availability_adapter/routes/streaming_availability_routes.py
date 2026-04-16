from fastapi import APIRouter
from controllers.streaming_availability_controller import get_movie_availability
from pydantic import BaseModel, Field
from typing import Any, Dict, List

router = APIRouter()


class StreamingService(BaseModel):
    service_name: str = Field(..., description="Name of the streaming service")
    service_type: str = Field(..., description="Type of service (Stream/Rent/Buy)")
    link: str = Field(..., description="URL to watch the movie")
    logo: str = Field(..., description="URL to service logo image")


class StreamingResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Dict[str, List[StreamingService]] = Field(
        ..., description="Streaming services grouped under a services key"
    )


SUCCESS_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Streaming services retrieved successfully",
    "data": {
        "services": [
            {
                "service_name": "Netflix",
                "service_type": "Stream",
                "link": "https://www.netflix.com/title/12345",
                "logo": "https://image.service.com/netflix-logo.png",
            },
            {
                "service_name": "Amazon Prime",
                "service_type": "Rent/Buy",
                "link": "https://www.amazon.com/movie/12345",
                "logo": "https://image.service.com/prime-logo.png",
            },
        ]
    },
}

ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    404: {"status": "error", "message": "No Streaming services found for this movie"},
    405: {"status": "error", "message": "Method not allowed"},
    422: {
        "status": "error",
        "code": 422,
        "message": "Request validation failed",
        "details": [
            {
                "field": "query -> imdb_id",
                "message": "field required",
                "type": "missing",
            }
        ],
    },
    429: {"status": "error", "message": "Streaming Availability API rate limit exceeded"},
    500: {"status": "error", "message": "Failed to connect to Streaming Availability API"},
    503: {"status": "error", "message": "Streaming Availability service is currently unavailable"},
    504: {"status": "error", "message": "Request to Streaming Availabiltiy API timed out"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Streaming services retrieved successfully",
    404: "No streaming services found",
    405: "Method not allowed",
    422: "Validation error",
    429: "API rate limit exceeded",
    500: "Internal server error",
    503: "Service unavailable",
    504: "Gateway timeout",
}

ROUTE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Streaming services found",
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
    "/api/v1/avail",
    response_model=StreamingResponse,
    summary="Get Movie Streaming Availability",
    description="Get streaming availability information for a movie by IMDB ID",
    responses=ROUTE_RESPONSES,
)(get_movie_availability)
