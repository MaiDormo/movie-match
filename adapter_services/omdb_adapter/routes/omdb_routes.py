from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.omdb_controller import get_movie_id, get_movies, health_check, get_movies_with_info
from pydantic import BaseModel, Field
from typing import Any, Dict, List

router = APIRouter()

class Movie(BaseModel):
    Title: str = Field(..., description="The full title of the movie as listed in OMDB")
    Year: str = Field(..., description="The release year of the movie in YYYY format")  
    imdbID: str = Field(..., description="Unique IMDB identifier starting with 'tt' followed by digits")
    Type: str = Field(..., description="The media type (e.g., 'movie', 'series', 'episode')")
    Director: str = Field(..., description="Name of the movie director(s)")
    Genre: str = Field(..., description="Comma-separated list of genres (e.g., 'Action, Adventure, Sci-Fi')")
    Poster: str = Field(..., description="URL to the movie poster image on IMDB")

    class Config:
        json_schema_extra = {
            "example": {
                "Title": "The Shawshank Redemption",
                "Year": "1994", 
                "imdbID": "tt0111161",
                "Type": "movie",
                "Director": "Frank Darabont",
                "Genre": "Drama",
                "Poster": "https://m.media-amazon.com/images/M/..."
            }
        }

class MovieDetails(Movie):
    imdbRating: str = Field(..., description="IMDB rating from 0 to 10 as a string (e.g., '8.5')")

    class Config:
        json_schema_extra = {
            "example": {
                "Title": "The Shawshank Redemption",
                "Year": "1994",
                "imdbID": "tt0111161", 
                "Type": "movie",
                "Director": "Frank Darabont",
                "Genre": "Drama",
                "Poster": "https://m.media-amazon.com/images/M/...",
                "imdbRating": "9.3"
            }
        }

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the operation result")

class MoviesResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the search operation")
    data: List[Movie] = Field(..., description="List of movies matching the search criteria")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Movies retrieved successfully",
                "data": [
                    {
                        "Title": "The Shawshank Redemption",
                        "Year": "1994",
                        "imdbID": "tt0111161",
                        "Type": "movie",
                        "Director": "Frank Darabont",
                        "Genre": "Drama",
                        "Poster": "https://m.media-amazon.com/images/M/..."
                    }
                ]
            }
        }

class MovieDetailsResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the movie details retrieval")
    data: MovieDetails = Field(..., description="Detailed information about a specific movie")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success", 
                "message": "Movie details retrieved successfully",
                "data": {
                    "Title": "The Shawshank Redemption",
                    "Year": "1994",
                    "imdbID": "tt0111161",
                    "Type": "movie",
                    "Director": "Frank Darabont", 
                    "Poster": "https://m.media-amazon.com/images/M/...",
                    "Genre": "Drama",
                    "imdbRating": "9.3"
                }
            }
        }

class MoviesWithInfoResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the movie search with details")
    data: List[MovieDetails] = Field(..., description="List of movies with additional details like genre and rating")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Movies retrieved successfully",
                "data": [
                    {
                        "Title": "The Shawshank Redemption",
                        "Year": "1994",
                        "imdbID": "tt0111161",
                        "Type": "movie",
                        "Director": "Frank Darabont",
                        "Poster": "https://m.media-amazon.com/images/M/...",
                        "Genre": "Drama",
                        "imdbRating": "9.3"
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


router.get(
    "/",
    response_class=JSONResponse,
    summary="Health Check",
    description="Health check endpoint to verify if the OMDB adapter service is running",
    response_model=BaseResponse,
    responses={
        200: {"description": "Service is up and running", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/search",
    response_class=JSONResponse,
    summary="Search Movies by Title",
    description="Search for movies by title using the OMDB API",
    response_model=MoviesResponse,
    responses={
        200: {"description": "Movies retrieved successfully", "model": MoviesResponse},
        404: {"description": "Movies not found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {
            "model": ErrorResponse,
            "description": "Validation Error"
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_movies)

router.get(
    "/api/v1/find",
    response_class=JSONResponse,
    summary="Get Movie Details by ID",
    description="Get detailed movie information by IMDB ID using the OMDB API",
    response_model=MovieDetailsResponse,
    responses={
        200: {"description": "Movie details retrieved successfully", "model": MovieDetailsResponse},
        404: {"description": "Movie not found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {
            "model": ErrorResponse,
            "description": "Validation Error"
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_movie_id)

router.get(
    "/api/v1/search_info",
    response_class=JSONResponse,
    summary="Search Movies with Additional Info",
    description="Search for movies by title and include additional details like genre and IMDb rating",
    response_model=MoviesWithInfoResponse,
    responses={
        200: {"description": "Movies retrieved successfully", "model": MoviesWithInfoResponse},
        404: {"description": "Movies not found", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {
            "model": ErrorResponse,
            "description": "Validation Error"
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_movies_with_info)