from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.movie_search_controller import get_user_genres, get_text_movie_search, update_user_preferences, get_genre_movie_search, health_check
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

router = APIRouter()

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class BaseResponseWithData(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data or error details")

class TextMovieList(BaseResponseWithData):
    data: Dict[str, Any] = Field(..., description="Movie list with relative details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Movies retrieved successfully",
                "data": {
                    "movie_list": [
                        {
                            "Title": "The Lord of the Rings: The Return of the King",
                            "Year": "2003",
                            "imdbID": "tt0167260",
                            "Poster": "https://image.tmdb.org/t/p/original//rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg",
                            "Genre": "Adventure, Fantasy, Action",
                            "imdbRating": 8.5
                        },
                        {
                            "Title": "The Lord of the Rings: The Fellowship of the Ring",
                            "Year": "2001",
                            "imdbID": "tt0120737",
                            "Poster": "https://image.tmdb.org/t/p/original//6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
                            "Genre": "Adventure, Fantasy, Action",
                            "imdbRating": 8.4
                        },
                        {
                            "Title": "Spider-Man: Across the Spider-Verse",
                            "Year": "2023",
                            "imdbID": "tt9362722",
                            "Poster": "https://image.tmdb.org/t/p/original//8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
                            "Genre": "Animation, Action, Adventure, Science Fiction",
                            "imdbRating": 8.4
                        }
                    ]
                }
            }
        }

class GenreMovieList(BaseResponseWithData):
    data: Dict[str, Any] = Field(..., description="Movie list with relative details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Movies retrieved successfully",
                "data": {
                    "movie_list": [
                        {
                            "Title": "Cars of the Revolution",
                            "Year": "2008",
                            "imdbID": "tt1282139",
                            "Type": "movie",
                            "Poster": "https://m.media-amazon.com/images/M/MV5BMmY0MzA0ODItNjUwZi00YjlmLTk5Y2EtY2E0NjJlNzVhMWQyXkEyXkFqcGc@._V1_SX300.jpg",
                            "Genre": "Drama, History",
                            "imdbRating": "8.0"
                        },
                        {
                            "Title": "Cars",
                            "Year": "2006",
                            "imdbID": "tt0317219",
                            "Type": "movie",
                            "Poster": "https://m.media-amazon.com/images/M/MV5BMTg5NzY0MzA2MV5BMl5BanBnXkFtZTYwNDc3NTc2._V1_SX300.jpg",
                            "Genre": "Animation, Adventure, Comedy",
                            "imdbRating": "7.3"
                        },
                        {
                            "Title": "Two Cars, One Night",
                            "Year": "2003",
                            "imdbID": "tt0390579",
                            "Type": "movie",
                            "Poster": "https://m.media-amazon.com/images/M/MV5BYmVjMmZkMTEtNGY5OC00MDFlLTk5NmYtYzQxMGIyNDI1MzBhXkEyXkFqcGc@._V1_SX300.jpg",
                            "Genre": "Short, Comedy, Drama",
                            "imdbRating": "7.2"
                        }
                    ]
                }
            }
        }

class GenreList(BaseResponseWithData):
    data: Dict[str, Any] = Field(..., description="Genre list and relative user preference")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Genres and user preferences retrieved successfully",
                "data": {
                    "user_genres": [
                        {
                            "genreId": 28,
                            "name": "Action",
                            "isPreferred": False
                        },
                        {
                            "genreId": 12,
                            "name": "Adventure",
                            "isPreferred": True
                        },
                        {
                            "genreId": 16,
                            "name": "Animation",
                            "isPreferred": False
                        },
                        {
                            "genreId": 35,
                            "name": "Comedy",
                            "isPreferred": False
                        },
                        {
                            "genreId": 80,
                            "name": "Crime",
                            "isPreferred": True
                        }
                    ]
                }
            }
        }

# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Movie Search Service is running",
    responses={
        200: {
            "description": "Service is running", 
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Movie Details Service is up and running!"
                    }
                }
            } 
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/user_genres",
    response_model=GenreList,
    summary="Get user Genres",
    description="Get a list of all the available genres, and for everyone of them the relative String description and whether it is one of the user's favorites",
    responses={
        200: {
            "description": "Genres retrieved successfully", 
            "model": GenreList
        },
        503: {
            "description": "Service unavailable",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "GENRE DATABASE service unavailable"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponseWithData
        }
    }
)(get_user_genres)

router.put(
    "/api/v1/update_user_genres",
    response_model=GenreList,
    summary="Update user Genres",
    description="Update the list of user favorite genres",
    responses={
        200: {
            "description": "Genres updated successfully", 
            "model": BaseResponseWithData,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User updated successfully",
                        "data": {
                            "_id": "0b8ac00c-a52b-4649-bd75-699b49c00ce3",
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "preferences": [
                                12
                            ],
                            "password": "$2b$12$00EMiNPHr9vxnUcwUy.GpuHFW8083fr02/DaWMgILAnil6pvwzZsy"
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponseWithData
        }
    }
)(update_user_preferences)

router.get(
    "/api/v1/movie_search_text",
    response_model=TextMovieList,
    summary="Text search",
    description="Get a list of movies by using a text search",
    responses={
        200: {
            "description": "Movies list retrieved successfully", 
            "model": TextMovieList
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponseWithData
        }
    }
)(get_text_movie_search)

router.get(
    "/api/v1/movie_search_genre",
    response_model=TextMovieList,
    summary="Genre search",
    description="Get a list of movies by using a genre search",
    responses={
        200: {
            "description": "Movies list retrieved successfully", 
            "model": TextMovieList
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponseWithData
        }
    }
)(get_genre_movie_search)