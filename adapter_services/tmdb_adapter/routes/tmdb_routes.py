from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.tmdb_controller import (
    discover_movies,
    get_movie_imdb_id,
    get_movie,
)
from pydantic import BaseModel, Field
from typing import Any, Dict, List

router = APIRouter()


class MovieDetails(BaseModel):
    Title: str = Field(..., description="Movie title")
    Year: str = Field(..., description="Release date in YYYY-MM-DD format")
    imdbId: str = Field(..., description="TMDB external IMDB identifier")
    Type: str = Field(..., description="Media type (typically 'movie')")
    GenreIds: List[Dict[str, Any]] | str = Field(
        ..., description="List of genre objects returned by TMDB"
    )
    Poster: str = Field(..., description="URL path to movie poster on TMDB")
    Rating: float = Field(..., description="TMDB rating from 0 to 10")


class DiscoverMovie(BaseModel):
    Title: str = Field(..., description="Movie title")
    Year: str = Field(..., description="Release date in YYYY-MM-DD format")
    tmdbId: int = Field(..., description="TMDB movie identifier")
    Type: str = Field(..., description="Media type (typically 'movie')")
    GenreIds: List[int] | str = Field(
        ..., description="List of genre IDs associated with the movie"
    )
    Poster: str = Field(..., description="URL path to movie poster on TMDB")
    Rating: float = Field(..., description="TMDB rating from 0 to 10")


class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")


class MovieIdData(BaseModel):
    imdb_id: str = Field(..., description="External IMDB identifier")


class MovieDetailsData(BaseModel):
    movie: MovieDetails = Field(..., description="Movie details payload")


class MoviesListData(BaseModel):
    total_results: int = Field(..., description="Total matching results")
    total_pages: int = Field(..., description="Total number of result pages")
    movie_list: List[DiscoverMovie] = Field(..., description="Discovered movies")


class MovieIDResponse(BaseResponse):
    data: MovieIdData = Field(..., description="Response containing IMDB ID")


class MovieResponse(BaseResponse):
    data: MovieDetailsData = Field(..., description="Movie details")


class MoviesListResponse(BaseResponse):
    data: MoviesListData = Field(
        ..., description="List of discovered movies with pagination info"
    )


SUCCESS_MOVIE_ID_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "IMDB ID retrieved successfully",
    "data": {"imdb_id": "tt1375666"},
}


ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    404: {"status": "error", "message": "Movie not found"},
    405: {"status": "error", "message": "Method not allowed"},
    422: {
        "status": "error",
        "code": 422,
        "message": "Request validation failed",
        "details": [
            {
                "field": "query -> id",
                "message": "field required",
                "type": "missing",
            }
        ],
    },
    500: {"status": "error", "message": "Internal server error occurred"},
    503: {"status": "error", "message": "TMDB API is currently unavailable"},
    504: {"status": "error", "message": "Request to TMDB API timed out"},
}


RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Success",
    404: "Not found",
    405: "Method not allowed",
    422: "Validation error",
    500: "Internal server error",
    503: "TMDB API unavailable",
    504: "Gateway Timeout",
}

MOVIE_ID_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "example": {
                    "summary": "Movie ID found",
                    "value": SUCCESS_MOVIE_ID_EXAMPLE,
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    MOVIE_ID_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }


router.get(
    "/api/v1/find-id",
    response_class=JSONResponse,
    response_model=MovieIDResponse,
    summary="Get IMDB ID",
    description="Get IMDB ID for a movie using TMDB ID",
    responses=MOVIE_ID_RESPONSES,
)(get_movie_imdb_id)

SUCCESS_DISCOVER_MOVIE_EXAMPLE: dict[str, Any] = {
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
                "GenreIds": [28, 878, 12],
                "Poster": "/8IB2e4r4oVhHnANbnm7O3Tj6tF8.jpg",
                "Rating": 8.4,
            }
        ],
    },
}

MOVIE_DISCOVER_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "example": {
                    "summary": "Movies retrieved successfully",
                    "value": SUCCESS_DISCOVER_MOVIE_EXAMPLE,
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    MOVIE_DISCOVER_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }

router.get(
    "/api/v1/discover-movies",
    response_class=JSONResponse,
    response_model=MoviesListResponse,
    summary="Discover Movies",
    description="Find movies based on genre, minimum rating and sort order",
    responses=MOVIE_DISCOVER_RESPONSES,
)(discover_movies)

SUCCESS_MOVIE_DETAILS_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Movie details retrieved successfully",
    "data": {
        "movie": {
            "Title": "Inception",
            "Year": "2010",
            "imdbId": "tt1375666",
            "Type": "movie",
            "GenreIds": [
                {"id": 28, "name": "Action"},
                {"id": 878, "name": "Science Fiction"},
            ],
            "Poster": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
            "Rating": 8.4,
        }
    },
}

MOVIE_DETAILS_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Movie found",
                        "value": SUCCESS_MOVIE_DETAILS_EXAMPLE,
                    }
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    MOVIE_DETAILS_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }

router.get(
    "/api/v1/movie",
    response_class=JSONResponse,
    response_model=MovieResponse,
    summary="Get Movie Details",
    description="Get detailed information about a movie by TMDB ID",
    responses=MOVIE_DETAILS_RESPONSES,
)(get_movie)
