from fastapi import APIRouter
from controllers.streaming_availability_controller import get_movie_availability, health_check
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class StreamingService(BaseModel):
    service_name: str = Field(..., description="Name of the streaming service")
    service_type: str = Field(..., description="Type of service (Stream/Rent/Buy)")
    link: str = Field(..., description="URL to watch the movie")
    logo: str = Field(..., description="URL to service logo image")

    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "Netflix",
                "service_type": "Stream",
                "link": "https://www.netflix.com/title/12345",
                "logo": "https://image.service.com/netflix-logo.png"
            }
        }

class StreamingResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: List[StreamingService] = Field(..., description="List of available streaming services")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Streaming availability retrieved successfully",
                "data": [
                    {
                        "service_name": "Netflix",
                        "service_type": "Stream",
                        "link": "https://www.netflix.com/title/12345",
                        "logo": "https://image.service.com/netflix-logo.png"
                    },
                    {
                        "service_name": "Amazon Prime",
                        "service_type": "Rent/Buy",
                        "link": "https://www.amazon.com/movie/12345",
                        "logo": "https://image.service.com/prime-logo.png"
                    }
                ]
            }
        }

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> imdb_id",
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
                        "field": "query -> imdb_id",
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
    description="Check if the Streaming Availability API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "Method not allowed", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/avail",
    response_model=StreamingResponse,
    summary="Get Movie Streaming Availability",
    description="Get streaming availability information for a movie by IMDB ID",
    responses={
        200: {"description": "Streaming availability retrieved successfully", "model": StreamingResponse},
        400: {"description": "Invalid request parameters", "model": BaseResponse},
        404: {"description": "Movie not found or no streaming availability", "model": BaseResponse},
        405: {"description": "Method not allowed", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        429: {"description": "API rate limit exceeded", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Streaming availability service unavailable", "model": BaseResponse},
        504: {"description": "Request to streaming availability service timed out", "model": BaseResponse}
    }
)(get_movie_availability)