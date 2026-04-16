from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from shared.common.response import create_response
from shared.common.http_utils import make_request

EXECUTOR = ThreadPoolExecutor(max_workers=4)


class MovieDetailsSettings(BaseModel):
    omdb_url: str = "http://omdb-adapter:5000"
    youtube_url: str = "http://youtube-adapter:5000"
    spotify_url: str = "http://spotify-adapter:5000"
    streaming_url: str = "http://streaming-availability-adapter:5000"
    trivia_url: str = "http://llm-adapter:5000"
    max_workers: int = 4


def get_settings() -> MovieDetailsSettings:
    return MovieDetailsSettings()


def _get_youtube_trailer(title: str, settings: MovieDetailsSettings) -> Optional[dict]:
    """Fetch Youtube trailer for movie."""
    try:
        result = make_request(
            f"{settings.youtube_url}/api/v1/get_video",
            params={"query": f"{title} trailer"},
        )
        if result.get("status") == "error":
            return None
        return result.get("data")
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None


def _get_spotify_playlist(title: str, settings: MovieDetailsSettings) -> Optional[dict]:
    """Fetch Spotify playlist for movie."""
    try:
        result = make_request(
            f"{settings.spotify_url}/api/v1/search_playlist",
            params={"playlist_name": title},
        )
        if result.get("status") == "error":
            return None
        return result.get("data")
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None


def _get_streaming_availability(
    imdb_id: str, settings: MovieDetailsSettings
) -> Optional[dict]:
    """Fetch streaming availability for movie."""
    try:
        result = make_request(
            f"{settings.streaming_url}/api/v1/avail",
            params={"imdb_id": imdb_id, "country": "it"},
        )
        if result.get("status") == "error":
            return None
        return result.get("data")
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None


def _get_movie_trivia(title: str, settings: MovieDetailsSettings) -> Optional[dict]:
    """Fetch AI trivia for movie."""
    try:
        result = make_request(
            f"{settings.trivia_url}/api/v1/get_trivia", params={"movie_title": title}
        )
        if result.get("status") == "error":
            return None
        return result.get("data")
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None


async def get_movie_details(
    id: str = Query(..., description="IMDB movie ID", example="tt4154796"),
    settings: MovieDetailsSettings = Depends(get_settings),
) -> JSONResponse:
    """Aggregate movie details from multiple services in parallel."""
    try:
        omdb_result = make_request(
            f"{settings.omdb_url}/api/v1/find", params={"id": id}
        )

        if omdb_result.get("status") == "error":
            return create_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message=omdb_result.get("message", "Failed to fetch movie data"),
            )

        movie_data = omdb_result.get("data", {})
        movie_title = movie_data.get("Title", "")

        # Parallel execution using ThreadPoolExecutor
        futures = [
            EXECUTOR.submit(_get_youtube_trailer, movie_title, settings),
            EXECUTOR.submit(_get_spotify_playlist, movie_title, settings),
            EXECUTOR.submit(_get_streaming_availability, id, settings),
            EXECUTOR.submit(_get_movie_trivia, movie_title, settings),
        ]

        youtube_trailer, spotify_playlist, streaming, trivia = [
            f.result() for f in futures
        ]

        service_data = {
            "omdb": movie_data,
            "youtube": youtube_trailer,
            "spotify": spotify_playlist,
            "streaming": streaming,
            "trivia": trivia,
        }

        available_services = sum(1 for v in service_data.values() if v is not None)

        if available_services == 0:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="All external services are currently unavailable",
            )

        message = (
            "Movie details retrieved successfully"
            if available_services == 5
            else "Movie details retrieved partially"
        )

        return create_response(
            status_code=status.HTTP_200_OK,
            message=message,
            data={"movie_details": service_data},
        )

    except HTTPError as e:
        return create_response(
            status_code=e.response.status_code, message=f"HTTP error occurred: {str(e)}"
        )
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="External service connection failed",
        )
    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to external service timed out",
        )
    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error fetching movie details: {str(e)}",
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
