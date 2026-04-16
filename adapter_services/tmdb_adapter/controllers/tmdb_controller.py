from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
import re

from shared.common.response import create_response
from shared.common.http_utils import make_request


# Models
class TMDBSettings(BaseModel):
    """TMDB API configuration Settings"""

    tmdb_url: str = Field(
        default="https://api.themoviedb.org/3/movie/", description="TMDB API base URL"
    )
    tmdb_discover_movie: str = Field(
        default="https://api.themoviedb.org/3/discover/movie",
        description="TMDB discover endpoint",
    )
    tmdb_api_key: Optional[str] = Field(
        default=os.getenv("TMDB_API_KEY"), description="TMDB API key from environment"
    )
    external_source: str = Field(
        default="imdb_id", description="External ID source type"
    )


# Helper Functions
def get_settings() -> TMDBSettings:
    """Dependency injection for TMDB configuration"""
    return TMDBSettings()


def _is_valid_language(language: str) -> bool:
    """Validate language format (e.g., en-US)"""
    pattern = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
    return bool(pattern.match(language))


# Data Filtering Functions
def _filter_id(tmdb_data: dict) -> str:
    """Extract IMDB ID from TMDB response"""
    if not tmdb_data.get("imdb_id"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No IMDB_ID found for {tmdb_data.get('id')}",
        )
    return tmdb_data["imdb_id"]


def _filter_movie_data(tmdb_data: dict) -> Dict[str, Any]:
    """Filter and format movie data"""
    return {
        "Title": tmdb_data.get("title", "N/A"),
        "Year": tmdb_data.get("release_date", "N/A"),
        "imdbId": tmdb_data.get("imdb_id", "N/A"),
        "Type": "movie",
        "GenreIds": tmdb_data.get("genres", "N/A"),
        "Poster": tmdb_data.get("poster_path", "N/A"),
        "Rating": tmdb_data.get("vote_average", "N/A"),
    }


def _filter_discover_movies(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter and format discovered movies list"""
    return [
        {
            "Title": movie.get("title", "N/A"),
            "Year": movie.get("release_date", "N/A"),
            "tmdbId": movie.get("id", "N/A"),
            "Type": "movie",
            "GenreIds": movie.get("genre_ids", "N/A"),
            "Poster": movie.get("poster_path", "N/A"),
            "Rating": movie.get("vote_average", "N/A"),
        }
        for movie in results
    ]


async def get_movie_imdb_id(
    id: int = Query(..., description="TMDB movie ID"),
    language: str = Query(..., description="Language code (e.g., en-US) [IETF BCP 47]"),
    TMDBSettings: TMDBSettings = Depends(get_settings),
) -> JSONResponse:
    """Get IMDB ID for a TMDB movie"""

    if not _is_valid_language(language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language format. Expected format: en-US, de-DE, it-IT, etc. [IETF BCP 47]",
        )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDBSettings.tmdb_api_key}",
    }

    try:
        response = make_request(
            f"{TMDBSettings.tmdb_url}{id}", headers=headers, data={"language": language}
        )
        imdb_id = _filter_id(response)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="IMDB ID retrieved successfully",
            data={"imdb_id": imdb_id},
        )

    except HTTPError as e:
        error_msg = f"HTTP error occured: {str(e)}"

        return create_response(status_code=e.response.status_code, message=error_msg)

    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="TMDB API is currently unavailable",
        )

    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to TMDB API timed out",
        )

    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling TMDB API: {str(e)}",
        )


async def get_movie(
    id: int = Query(..., description="TMDB movie ID"),
    language: str = Query(..., description="Language code (e.g., en-US) [IETF BCP 47]"),
    TMDBSettings: TMDBSettings = Depends(get_settings),
) -> JSONResponse:
    """Get movie details by TMDB ID"""

    if not _is_valid_language(language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language format. Expected format: en-US, de-DE, it-IT, etc. [IETF BCP 47]",
        )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDBSettings.tmdb_api_key}",
    }

    try:
        response = make_request(
            f"{TMDBSettings.tmdb_url}{id}", headers=headers, data={"language": language}
        )
        movie_data = _filter_movie_data(response)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movie details retrieved successfully",
            data={"movie": movie_data},
        )

    except HTTPError as e:
        error_msg = f"HTTP error occured: {str(e)}"

        return create_response(status_code=e.response.status_code, message=error_msg)

    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="TMDB API is currently unavailable",
        )

    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to TMDB API timed out",
        )

    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling TMDB API: {str(e)}",
        )


async def discover_movies(
    language: str = Query(..., description="Language code (e.g., en-US) [IETF BCP 47]"),
    with_genres: str = Query(..., description="Comma-separated list of genre IDs"),
    vote_avg_gt: float = Query(..., description="Minimum vote average"),
    sort_by: str = Query(
        default="popularity.desc", description="Sort order for results"
    ),
    TMDBSettings: TMDBSettings = Depends(get_settings),
) -> JSONResponse:
    """Discover movies by genres and rating"""
    if not _is_valid_language(language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language format. Expected format: en-US, de-DE, it-IT, etc. [IETF BCP 47]",
        )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDBSettings.tmdb_api_key}",
    }

    params = {
        "language": language,
        "with_genres": with_genres,
        "vote_average.gte": vote_avg_gt,
        "sort_by": sort_by,
        "include_adult": False,
        "include_video": False,
        "page": 1,
        "vote_count.gte": 100,
    }

    try:
        movies = make_request(TMDBSettings.tmdb_discover_movie, headers=headers, params=params)

        if not movies.get("results"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No movies found matching the criteria",
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies retrieved successfully",
            data={
                "total_results": movies["total_results"],
                "total_pages": movies["total_pages"],
                "movie_list": _filter_discover_movies(movies["results"]),
            },
        )

    except HTTPError as e:
        error_msg = f"HTTP error occured: {str(e)}"

        return create_response(status_code=e.response.status_code, message=error_msg)

    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="TMDB API is currently unavailable",
        )

    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to TMDB API timed out",
        )

    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling TMDB API: {str(e)}",
        )
