from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.omdb_controller import get_movie_id, get_movies, health_check, get_movies_with_info
from pydantic import BaseModel
from typing import Any, Dict, List

router = APIRouter()

class Movie(BaseModel):
    Title: str
    Year: str
    imdbID: str
    Type: str
    Poster: str

class MovieDetails(Movie):
    Genre: str
    imdbRating: str

class GenralResponse(BaseModel):
    status: str
    message: str

class MoviesResponse(BaseModel):
    status: str
    message: str
    data: List[Movie]

class MovieDetailsResponse(BaseModel):
    status: str
    message: str
    data: MovieDetails

class MoviesWithInfoResponse(BaseModel):
    status: str
    message: str
    data: List[MovieDetails]

router.get(
    "/",
    response_class=JSONResponse,
    summary="Health Check",
    description="Health check endpoint to verify if the OMDB adapter service is running",
    responses={
        200: {"description": "Service is up and running", "model": GenralResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": GenralResponse},
        500: {"description": "Internal server error", "model": GenralResponse}
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
        404: {"description": "Movies not found", "model": GenralResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": GenralResponse},
        500: {"description": "Internal server error", "model": GenralResponse}
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
        404: {"description": "Movie not found", "model": GenralResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": GenralResponse},
        500: {"description": "Internal server error", "model": GenralResponse}
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
        404: {"description": "Movies not found", "model": GenralResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": GenralResponse},
        500: {"description": "Internal server error", "model": GenralResponse}
    }
)(get_movies_with_info)