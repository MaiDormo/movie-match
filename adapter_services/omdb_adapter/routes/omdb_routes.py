from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.omdb_controller import get_movie_id, get_movies_with_info
from pydantic import BaseModel, Field
from typing import Any, Dict, List

router = APIRouter()

class Movie(BaseModel):
    Title: str = Field(..., description="The full title of the movie as listed in OMDB")
    Year: str = Field(..., description="The release year of the movie in YYYY format")
    imdbID: str = Field(
        ..., description="Unique IMDB identifier starting with 'tt' followed by digits"
    )
    Type: str = Field(
        ..., description="The media type (e.g., 'movie', 'series', 'episode')"
    )
    Director: str = Field(..., description="Name of the movie director(s)")
    Genre: str = Field(..., description="Comma-separated list of genres")
    Poster: str = Field(..., description="URL to the movie poster image on IMDB")


class MovieDetails(Movie):
    imdbRating: str = Field(..., description="IMDB rating from 0 to 10 as a string")


class MovieDetailsResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(
        ..., description="Descriptive message about the movie details retrieval"
    )
    data: MovieDetails = Field(
        ..., description="Detailed information about a specific movie"
    )


class MoviesWithInfoResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(
        ..., description="Descriptive message about the movie search with details"
    )
    data: Dict[str, List[MovieDetails]] = Field(
        ..., description="Movies wrapped in a data object"
    )


SUCCESS_MOVIE_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Movie details retrieved successfully",
    "data": {
        "Title": "The Shawshank Redemption",
        "Year": "1994",
        "imdbID": "tt0111161",
        "Type": "movie",
        "Director": "Frank Darabont",
        "Genre": "Drama",
        "Poster": "https://m.media-amazon.com/images/M/...",
        "imdbRating": "9.3",
    },
}

SUCCESS_SEARCH_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Movies retrieved successfully",
    "data": {
        "movies": [
            {
                "Title": "The Shawshank Redemption",
                "Year": "1994",
                "imdbID": "tt0111161",
                "Type": "movie",
                "Director": "Frank Darabont",
                "Genre": "Drama",
                "Poster": "https://m.media-amazon.com/images/M/...",
                "imdbRating": "9.3",
            }
        ]
    },
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
    503: {"status": "error", "message": "OMDB API is currently unavailable"},
    504: {"status": "error", "message": "Request to OMDB API timed out"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Success",
    404: "Not found",
    405: "Method not allowed",
    422: "Validation error",
    500: "Internal server error",
    503: "OMDB API unavailable",
    504: "Gateway timeout",
}

MOVIE_DETAILS_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Movie found",
                        "value": SUCCESS_MOVIE_EXAMPLE,
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

MOVIES_WITH_INFO_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Movies found",
                        "value": SUCCESS_SEARCH_EXAMPLE,
                    }
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    MOVIES_WITH_INFO_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }

router.get(
    "/api/v1/find",
    response_class=JSONResponse,
    summary="Get Movie Details by ID",
    description="Get detailed movie information by IMDB ID using the OMDB API",
    response_model=MovieDetailsResponse,
    responses=MOVIE_DETAILS_RESPONSES,
)(get_movie_id)

router.get(
    "/api/v1/search_info",
    response_class=JSONResponse,
    summary="Search Movies with Additional Info",
    description="Search for movies by title and include additional details like genre and IMDb rating",
    response_model=MoviesWithInfoResponse,
    responses=MOVIES_WITH_INFO_RESPONSES,
)(get_movies_with_info)

