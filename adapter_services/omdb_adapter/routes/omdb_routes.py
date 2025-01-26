from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.omdb_controller import get_movie_id, health_check, get_movies_with_info
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
class MovieDetails(Movie):
    imdbRating: str = Field(..., description="IMDB rating from 0 to 10 as a string (e.g., '8.5')")

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the operation result")

class MoviesResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the search operation")
    data: List[Movie] = Field(..., description="List of movies matching the search criteria")

class MovieDetailsResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the movie details retrieval")
    data: MovieDetails = Field(..., description="Detailed information about a specific movie")

class MoviesWithInfoResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Descriptive message about the movie search with details")
    data: List[MovieDetails] = Field(..., description="List of movies with additional details like genre and rating")

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: List[ValidationError] | Dict[str, Any] | None = None


router.get(
    "/",
    response_class=JSONResponse,
    summary="Health Check",
    description="Health check endpoint to verify if the OMDB adapter service is running",
    response_model=BaseResponse,
    responses={
        200: {
            "description": "Service is up and running",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Service healthy",
                            "value": {
                                "status": "success",
                                "message": "OMDB API Adapter is up and running!"
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
        },
        503: {
            "description": "OMDB API is currently unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "OMDB API is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Request to OMDB API timed out",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to OMDB API timed out"
                    }
                }
            }
        }
    }
)(health_check)

router.get(
    "/api/v1/find",
    response_class=JSONResponse,
    summary="Get Movie Details by ID",
    description="Get detailed movie information by IMDB ID using the OMDB API",
    response_model=MovieDetailsResponse,
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
                        }
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
            "description": "Validation Error",
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
            "description": "OMDB API is currently unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "OMDB API is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Request to OMDB API timed out",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to OMDB API timed out"
                    }
                }
            }
        }
    }
)(get_movie_id)

router.get(
    "/api/v1/search_info",
    response_class=JSONResponse,
    summary="Search Movies with Additional Info",
    description="Search for movies by title and include additional details like genre and IMDb rating",
    response_model=MoviesWithInfoResponse,
    responses={
        200: {
            "description": "Movies retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Movies found",
                            "value": {
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
                                        "Poster": "https://m.media-amazon.com/images/M/...",
                                        "imdbRating": "9.3"
                                    }
                                ]
                            }
                        }
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
                        "message": "No movies found"
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
            "description": "Validation Error",
            "content": {
                "application/json": {
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
            "description": "OMDB API is currently unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "OMDB API is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Request to OMDB API timed out",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to OMDB API timed out"
                    }
                }
            }
        }
    }
)(get_movies_with_info)