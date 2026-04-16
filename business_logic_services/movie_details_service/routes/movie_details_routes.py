from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.movie_details_controller import get_movie_details
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

router = APIRouter()


class MovieDetailsResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(
        ..., description="Detailed information about the movie"
    )


SUCCESS_MOVIE_DETAILS_EXAMPLE: dict[str, Any] = {
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
                "Poster": "https://m.media-amazon.com/images/M/...",
                "imdbRating": "8.4",
            },
            "youtube": {
                "video_id": "TcMBFSGVi1c",
                "embed_url": "https://www.youtube.com/embed/TcMBFSGVi1c",
            },
            "spotify": {
                "spotify_url": "https://open.spotify.com/playlist/...",
                "cover_url": "https://image-cdn-ak.spotifycdn.com/...",
                "name": "Avengers: Endgame Soundtrack Official Playlist",
            },
            "streaming": {
                "services": [
                    {
                        "service_name": "Disney+",
                        "service_type": "Subscription",
                        "link": "https://www.disneyplus.com/...",
                        "logo": "https://media.movieofthenight.com/...",
                    }
                ]
            },
            "trivia": {
                "question": "Who directed Avengers: Endgame?",
                "options": ["Anthony Russo, Joe Russo", "Joss Whedon", "James Gunn"],
                "correct_answer": "Anthony Russo, Joe Russo",
            },
        }
    },
}

ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    404: {"status": "error", "message": "Movie not found"},
    502: {"status": "error", "message": "Failed to fetch movie data"},
    503: {
        "status": "error",
        "message": "All external services are currently unavailable",
    },
    500: {"status": "error", "message": "Internal server error"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Success",
    404: "Not found",
    502: "Bad Gateway",
    503: "Service unavailable",
    500: "Internal server error",
}

MOVIE_DETAILS_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Movie details retrieved",
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
    "/api/v1/movie_details",
    response_class=JSONResponse,
    summary="Get Movie Details",
    description="Retrieve detailed information about a movie, including streaming availability, YouTube trailers, Spotify playlists, and trivia questions.",
    response_model=MovieDetailsResponse,
    responses=MOVIE_DETAILS_RESPONSES,
)(get_movie_details)
