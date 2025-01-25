from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.movie_details_controller import get_movie_details, health_check
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

    class Config:
        extra = 'forbid'  # Prevents additional fields
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Movie not found"
            }
        }

class BaseResponseWithData(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data or error details")

class MovieDetailsResponse(BaseResponseWithData):
    data: Dict[str, Any] = Field(..., description="Detailed information about the movie")

    class Config:
        json_schema_extra = {
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


# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Movie Details Service is running",
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
    "/api/v1/movie_details",
    response_model=MovieDetailsResponse,
    summary="Get Movie Details",
    description="Retrieve detailed information about a movie, including streaming availability, YouTube trailers, Spotify playlists, and trivia questions.",
    responses={
        200: {"description": "Movie details retrieved successfully", "model": MovieDetailsResponse},
        404: {
            "description": "Movie not found",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Incorrect IMDb ID."
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "All services are currently unavailable"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponseWithData,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "An unexpected error occurred",
                        "data": {
                            "error": "get expected at least 1 argument, got 0"
                        }
                    }
                }
            }
        }
    }
)(get_movie_details)