from fastapi import APIRouter
from controllers.genre_db_controller import create_genre, list_genres, get_genre, update_genre, delete_genre, health_check 
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class GenreBase(BaseModel):
    genreId: int = Field(..., description="Unique identifier for the genre")
    name: str = Field(..., description="The name of the genre")

    class Config:
        json_schema_extra = {
            "example": {
                "genreId": 28,
                "name": "Action"
            }
        }

class GenreListResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="List of genres with count")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Genres retrieved successfully",
                "data": {
                    "total": 2,
                    "genres": [
                        {"genreId": 28, "name": "Action"},
                        {"genreId": 35, "name": "Comedy"}
                    ]
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
                "field": "body -> name",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[List[ValidationError]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "body -> name",
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
    description="Check if the Genres DB API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "Method not allowed", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.post(
    "/api/v1/genre",
    status_code=201,
    response_model=BaseResponse,
    summary="Create Genre",
    description="Create a new genre in the database",
    responses={
        201: {"description": "Genre created successfully", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Database connection error", "model": BaseResponse}
    }
)(create_genre)

router.get(
    "/api/v1/genres",
    response_model=GenreListResponse,
    summary="List Genres",
    description="Get list of all available genres",
    responses={
        200: {"description": "Genres retrieved successfully", "model": GenreListResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Database connection error", "model": BaseResponse}
    }
)(list_genres)

router.get(
    "/api/v1/genre",
    response_model=BaseResponse,
    summary="Get Genre",
    description="Get a specific genre by ID",
    responses={
        200: {"description": "Genre retrieved successfully", "model": BaseResponse},
        404: {"description": "Genre not found", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Database connection error", "model": BaseResponse}
    }
)(get_genre)

router.put(
    "/api/v1/genre",
    response_model=BaseResponse,
    summary="Update Genre",
    description="Update an existing genre by ID",
    responses={
        200: {"description": "Genre updated successfully", "model": BaseResponse},
        404: {"description": "Genre not found", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Database connection error", "model": BaseResponse}
    }
)(update_genre)

router.delete(
    "/api/v1/genre",
    status_code=204,
    summary="Delete Genre",
    description="Delete a genre by ID",
    responses={
        204: {"description": "Genre deleted successfully"},
        404: {"description": "Genre not found", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        503: {"description": "Database connection error", "model": BaseResponse}
    }
)(delete_genre)