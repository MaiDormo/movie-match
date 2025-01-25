from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from controllers.movie_match_controller import (
    health_check,
    get_movie_details,
    get_user_genres,
    update_user_genres,
    get_movie_search_by_text,
    get_genre_movie_search_by_url
)

router = APIRouter()

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class BaseResponseWithData(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data or error details")


# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Movie Match Service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Movie Match Service is up and running!"
                    }
                }
            }
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/movies",
    response_model=BaseResponseWithData,
    summary="Get Movie Details",
    description="Retrieve details about a specific movie.",
    responses={
        200: {
            "description": "Movie details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Movie details retrieved successfully",
                        "data": {
                            "movie_details": {
                                "omdb": {
                                    "Title": "Avengers: Endgame",
                                    "Year": "2019",
                                    "imdbID": "tt4154796",
                                    "Type": "movie",
                                    "Director": "Anthony Russo, Joe Russo",
                                    "Genre": "Action, Adventure, Drama",
                                    "Poster": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg",
                                    "imdbRating": "8.4"
                                },
                                "youtube": {
                                    "status": "success",
                                    "message": "YouTube video retrieved successfully",
                                    "data": {
                                        "video_id": "TcMBFSGVi1c",
                                        "embed_url": "https://www.youtube.com/embed/TcMBFSGVi1c"
                                    }
                                },
                                "spotify": {
                                    "status": "success",
                                    "message": "Playlist found successfully",
                                    "data": {
                                        "spotify_url": "https://open.spotify.com/playlist/085SdQYERg63mWDVK3Xwi9",
                                        "cover_url": "https://image-cdn-ak.spotifycdn.com/image/ab67706c0000da8481be56f5be03e95f0cd4cc8",
                                        "name": "Avengers: Endgame Soundtrack Official Playlist"
                                    }
                                },
                                "streaming": {
                                    "status": "success",
                                    "message": "Streaming availability retrieved successfully",
                                    "data": [
                                        {
                                            "service_name": "Apple TV",
                                            "service_type": "Buy",
                                            "link": "https://tv.apple.com/it/movie/avengers-endgame/umc.cmc.4ao9tm6b6rz4sy7yj5v13ltf8?playableId=tvs.sbd.9001%3A1459466643",
                                            "logo": "https://media.movieofthenight.com/services/apple/logo-light-theme.svg"
                                        },
                                        {
                                            "service_name": "Disney+",
                                            "service_type": "Subscription",
                                            "link": "https://www.disneyplus.com/movies/marvel-studios-avengers-endgame/aRbVJUb2h2Rf",
                                            "logo": "https://media.movieofthenight.com/services/disney/logo-light-theme.svg"
                                        },
                                        {
                                            "service_name": "Prime Video",
                                            "service_type": "Buy/Rent",
                                            "link": "https://www.primevideo.com/detail/0OI091IRNAIWL6HY536UZ1JA6O/ref=atv_dp",
                                            "logo": "https://media.movieofthenight.com/services/prime/logo-light-theme.svg"
                                        }
                                    ]
                                },
                                "trivia": {
                                    "status": "success",
                                    "message": "Trivia question generated successfully",
                                    "ai_question": "In the film Avengers: Endgame, what is the name of the plan devised by the surviving Avengers to undo the damage caused by Thanos?\n\n1. The Quantum Plan\n2. The Time Travel Initiative\n3. The Infinity Gauntlet Scheme\n\n",
                                    "ai_answer": "3"
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "Movie not found", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_movie_details)

router.get(
    "/api/v1/user-genres",
    response_model=BaseResponseWithData,
    summary="Get User Genres",
    description="Retrieve the list of genres and user preferences.",
    responses={
        200: {
            "description": "Genres retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_user_genres)

router.put(
    "/api/v1/user-genres/update",
    response_model=BaseResponseWithData,
    summary="Update User Genres",
    description="Update the list of user favorite genres.",
    responses={
        200: {
            "description": "Genres updated successfully",
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
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(update_user_genres)

router.get(
    "/api/v1/movies/search-by-text",
    response_model=BaseResponseWithData,
    summary="Search Movies by Text",
    description="Search for movies using a text query.",
    responses={
        200: {
            "description": "Movies retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_movie_search_by_text)

router.get(
    "/api/v1/movies/search-by-genre",
    response_model=BaseResponseWithData,
    summary="Search Movies by Genre",
    description="Search for movies by selecting specific genres.",
    responses={
        200: {
            "description": "Movies retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(get_genre_movie_search_by_url)
