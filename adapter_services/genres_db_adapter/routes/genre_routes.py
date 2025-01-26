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

class GenreListResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="List of genres with count")

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[List[ValidationError]] = None

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Genres DB API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Genres DB API adapter is up and running"
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

router.post(
    "/api/v1/genre",
    status_code=201,
    response_model=BaseResponse,
    summary="Create Genre",
    description="Create a new genre in the database",
    responses={
        201: {
            "description": "Genre created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Genre created successfully",
                        "data": {"genreId": 28, "name": "Action"}
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
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error", 
                        "message": "Genre with this ID already exists"
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
                                "field": "body -> name",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
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
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(create_genre)

router.get(
    "/api/v1/genres",
    response_model=GenreListResponse,
    summary="List Genres",
    description="Get list of all available genres",
    responses={
        200: {
            "model": GenreListResponse,
            "description": "Genres retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        404: {
            "description": "Genres not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Genres not found"
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
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(list_genres)

router.get(
    "/api/v1/genre",
    response_model=BaseResponse,
    summary="Get Genre", 
    description="Get a specific genre by ID",
    responses={
        200: {
            "description": "Genre retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Genre retrieved successfully",
                        "data": {
                            "genreId": 28,
                            "name": "Action"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Genre not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error", 
                        "message": "Genre not found"
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
                                "field": "query -> id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
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
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(get_genre)

router.put(
    "/api/v1/genre",
    response_model=BaseResponse,
    summary="Update Genre",
    description="Update an existing genre by ID",
    responses={
        200: {
            "description": "Genre updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Genre updated successfully",
                        "data": {
                            "genreId": 28,
                            "name": "Action & Adventure"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Genre not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Genre not found"
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
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Genre with this ID already exists"
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
                                "field": "body -> name",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
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
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(update_genre)

router.delete(
    "/api/v1/genre",
    status_code=204,
    summary="Delete Genre",
    description="Delete a genre by ID",
    responses={
        204: {
            "description": "Genre deleted successfully"
        },
        404: {
            "description": "Genre not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Genre not found"
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
                                "field": "query -> id",
                                "message": "field required", 
                                "type": "missing"
                            }
                        ]
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
        },
        503: {
            "description": "Database connection error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Database connection error"
                    }
                }
            }
        }
    }
)(delete_genre)