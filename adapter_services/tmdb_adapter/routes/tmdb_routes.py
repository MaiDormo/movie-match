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

    class Config:
        json_schema_extra = {
            "example": {
                "Title": "Inception",
                "Year": "2010",
                "tmdbId": 27205,
                "Type": "movie",
                "Poster": "/8IB2e4r4oVhHnANbnm7O3Tj6tF8.jpg",
                "Rating": 8.4
            }
        }

class MovieWithGenres(MovieBase):
    GenresIds: List[int] = Field(..., description="List of genre IDs associated with the movie")

    class Config:
        json_schema_extra = {
            "example": {
                "Title": "Inception",
                "Year": "2010",
                "imdbId": "tt1375666",
                "Type": "movie",
                "Poster": "/8IB2e4r4oVhHnANbnm7O3Tj6tF8.jpg",
                "Rating": 8.4,
                "GenresIds": [28, 878, 12]
            }
        }

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class MovieIDResponse(BaseResponse):
    data: dict = Field(..., description="Response containing IMDB ID")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "IMDB ID retrieved successfully",
                "data": {
                    "imdb_id": "tt1375666"
                }
            }
        }

class MovieResponse(BaseResponse):
    data: dict = Field(..., description="Movie details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Movie details retrieved successfully",
                "data": {
                    "movie": {
                    "Title": "Mufasa: The Lion King",
                    "Year": "2024-12-18",
                    "imdbId": "tt13186482",
                    "Type": "movie",
                    "GenreIds": [
                        {
                        "id": 12,
                        "name": "Adventure"
                        },
                        {
                        "id": 10751,
                        "name": "Family"
                        },
                        {
                        "id": 16,
                        "name": "Animation"
                        }
                    ],
                    "Poster": "/jbOSUAWMGzGL1L4EaUF8K6zYFo7.jpg",
                    "Rating": 7.427
                    }
                }
            }
        }

class MoviesListResponse(BaseResponse):
    data: dict = Field(..., description="List of discovered movies with pagination info")

    class Config:
        json_schema_extra = {
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

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> title",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: List[ValidationError] | Dict[str, Any] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "query -> title",
                        "message": "field required",
                        "type": "missing"
                    }
                ]
            }
        }

# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the TMDB API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        504: {"description": "Request to TMDB API timed out", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/find-id",
    response_model=MovieIDResponse,
    summary="Get IMDB ID",
    description="Get IMDB ID for a movie using TMDB ID",
    responses={
        200: {"description": "IMDB ID retrieved successfully", "model": MovieIDResponse},
        400: {"description": "Invalid request parameters", "model": BaseResponse},
        404: {"description": "Movie not found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        503: {"description": "TMDB service unavailable", "model": BaseResponse},
        504: {"description": "Request to TMDB API timed out", "model": BaseResponse}
    }
)(get_movie_imdb_id)

router.get(
    "/api/v1/discover-movies",
    response_model=MoviesListResponse,
    summary="Discover Movies",
    description="Find movies based on genre, minimum rating and sort order",
    responses={
        200: {"description": "Movies retrieved successfully", "model": MoviesListResponse},
        400: {"description": "Invalid request parameters", "model": BaseResponse},
        404: {"description": "No movies found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        503: {"description": "TMDB service unavailable", "model": BaseResponse},
        504: {"description": "Request to TMDB API timed out", "model": BaseResponse}
    }
)(discover_movies)

router.get(
    "/api/v1/movie",
    response_model=MovieResponse,
    summary="Get Movie Details",
    description="Get detailed information about a movie by TMDB ID",
    responses={
        200: {"description": "Movie details retrieved successfully", "model": MovieResponse},
        400: {"description": "Invalid request parameters", "model": BaseResponse},
        404: {"description": "Movie not found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        503: {"description": "TMDB service unavailable", "model": BaseResponse},
        504: {"description": "Request to TMDB API timed out", "model": BaseResponse}
    }
)(get_movie)