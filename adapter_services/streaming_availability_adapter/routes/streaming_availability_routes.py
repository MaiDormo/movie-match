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

class StreamingResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: List[StreamingService] = Field(..., description="List of available streaming services")

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Streaming Availability API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Service is healthy",
                            "value": {
                                "status": "success",
                                "message": "Streaming Availability API adapter is up and running"
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
                        "message": "Method not allowed"
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
    "/api/v1/avail",
    response_model=StreamingResponse,
    summary="Get Movie Streaming Availability",
    description="Get streaming availability information for a movie by IMDB ID",
    responses={
        200: {
            "description": "Streaming availability retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid IMDB ID format"
                    }
                }
            }
        },
        404: {
            "description": "Movie not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Movie not found"
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
                                "field": "query -> imdb_id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "API rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "API rate limit exceeded. Please try again later."
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Streaming availability service is currently unavailable"
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
                        "message": "Request to streaming availability service timed out"
                    }
                }
            }
        }
    }
)(get_movie_availability)