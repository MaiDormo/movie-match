from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.tmdb_controller import discover_movies, get_movie_imdb_id, get_movie, health_check
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

router = APIRouter()

# Response Models
class MovieBase(BaseModel):
    Title: str = Field(..., description="Movie title")
    Year: str = Field(..., description="Release year (YYYY)")
    imdbId: str = Field(..., description="TMDB unique identifier")
    Type: str = Field(..., description="Media type (typically 'movie')")
    Poster: str = Field(..., description="URL path to movie poster on TMDB")
    Rating: float = Field(..., description="TMDB rating from 0 to 10")

class MovieWithGenres(MovieBase):
    GenresIds: List[int] = Field(..., description="List of genre IDs associated with the movie")

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class MovieIDResponse(BaseResponse):
    data: dict = Field(..., description="Response containing IMDB ID")

class MovieResponse(BaseResponse):
    data: dict = Field(..., description="Movie details")

class MoviesListResponse(BaseResponse):
    data: dict = Field(..., description="List of discovered movies with pagination info")

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: List[ValidationError] | Dict[str, Any] | None = None

# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the TMDB API adapter service is running",
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
                                "message": "TMDB API adapter is up and running"
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
    "/api/v1/find-id",
    response_model=MovieIDResponse,
    summary="Get IMDB ID",
    description="Get IMDB ID for a movie using TMDB ID",
    responses={
        200: {
            "description": "IMDB ID retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "IMDB ID retrieved successfully",
                        "data": {
                            "imdb_id": "tt1375666"
                        }
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
                        "message": "Invalid TMDB ID format"
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
        405: {
            "description": "The HTTP method is not allowed for this endpoint",
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
                                "field": "query -> tmdb_id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        503: {
            "description": "TMDB service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "TMDB service is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Request to TMDB API timed out",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to TMDB API timed out"
                    }
                }
            }
        }
    }
)(get_movie_imdb_id)

router.get(
    "/api/v1/discover-movies",
    response_model=MoviesListResponse,
    summary="Discover Movies",
    description="Find movies based on genre, minimum rating and sort order",
    responses={
        200: {
            "description": "Movies retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Movies retrieved successfully",
                        "data": {
                            "total_results": 42,
                            "total_pages": 3,
                            "movie_list": [
                                {
                                    "Title": "Inception",
                                    "Year": "2010",
                                    "tmdbId": 27205,
                                    "Type": "movie",
                                    "GenresIds": [28, 878, 12],
                                    "Poster": "/8IB2e4r4oVhHnANbnm7O3Tj6tF8.jpg",
                                    "Rating": 8.4
                                }
                            ]
                        }
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
                        "message": "Invalid genre ID format"
                    }
                }
            }
        },
        404: {
            "description": "No movies found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "No movies found for the provided query"
                    }
                }
            }
        },
        405: {
            "description": "The HTTP method is not allowed for this endpoint",
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
                                "field": "query -> genre_id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        503: {
            "description": "TMDB service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "TMDB service is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Request to TMDB API timed out",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to TMDB API timed out"
                    }
                }
            }
        }
    }
)(discover_movies)

router.get(
    "/api/v1/movie",
    response_model=MovieResponse,
    summary="Get Movie Details",
    description="Get detailed information about a movie by TMDB ID",
    responses={
        200: {
            "description": "Movie details retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Movie found",
                            "value": {
                                "status": "success",
                                "message": "Movie details retrieved successfully",
                                "data": {
                                    "Title": "Inception",
                                    "Year": "2010",
                                    "imdbID": "tt1375666",
                                    "Type": "movie",
                                    "Director": "Christopher Nolan",
                                    "Genre": "Action, Adventure, Sci-Fi",
                                    "Poster": "https://image.tmdb.org/t/p/original/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
                                    "Rating": 8.4
                                }
                            }
                        }
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
                        "message": "Invalid TMDB ID format"
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
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> tmdb_id",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        503: {
            "description": "TMDB service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "TMDB service is currently unavailable"
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
                        "message": "Request to TMDB API timed out"
                    }
                }
            }
        }
    }
)(get_movie)