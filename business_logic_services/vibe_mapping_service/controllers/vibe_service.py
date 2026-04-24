import random
from pathlib import Path
from typing import Any

import httpx
import yaml
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from controllers.spin_calculator import get_random_sort
from controllers.vibe_mapper import CONFIG_PATH, get_genres, list_vibes
from shared.common.response import create_response

_CONFIG = yaml.safe_load(Path(CONFIG_PATH).read_text(encoding="utf-8"))


class VibeSettings(BaseModel):
    movie_search_url: str = "http://movie-search-service:5000/api/v1/movie_search_genre"
    timeout: float = 15.0


def _get_settings() -> VibeSettings:
    return VibeSettings()


def get_all_vibes() -> JSONResponse:
    return create_response(
        status_code=status.HTTP_200_OK,
        message="List of mapped vibes genres",
        data={"vibes": list_vibes()},
    )


async def get_movie_by_vibe(
    vibes: str = Query(...),
    settings: VibeSettings = Depends(_get_settings),
) -> JSONResponse:
    vibe_list = [v.strip().lower() for v in vibes.split(",") if v.strip()]
    if not vibe_list:
        return create_response(status.HTTP_400_BAD_REQUEST, "No vibes provided")

    invalid: list[str] = []
    genre_ids: set[int] = set()
    for vibe in vibe_list:
        genres = get_genres(vibe)
        if not genres:
            invalid.append(vibe)
            continue
        genre_ids.update(genres)

    if invalid:
        return create_response(
            status.HTTP_400_BAD_REQUEST,
            "Invalid vibes requested",
            {"invalid_vibes": invalid},
        )

    params = {
        "with_genres": ",".join(map(str, sorted(genre_ids))),
        "vote_avg_gt": 0,
        "language": "en-US",
        "sort_by": get_random_sort(_CONFIG),
    }

    try:
        async with httpx.AsyncClient(timeout=settings.timeout) as client:
            response = await client.get(settings.movie_search_url, params=params)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except httpx.TimeoutException:
        return create_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Movie search service timed out",
        )
    except httpx.HTTPStatusError:
        return create_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Movie search service unavailable",
        )
    except Exception as exc:
        return create_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Internal error: {str(exc)}",
        )

    if data.get("status") == "error":
        return create_response(
            status.HTTP_502_BAD_GATEWAY,
            "Movie search service returned error",
        )

    movies = data.get("data", {}).get("movie_list", [])
    if not isinstance(movies, list):
        movies = []

    random.shuffle(movies)
    return create_response(
        status.HTTP_200_OK,
        "Movies retrieved successfully",
        {"movie_list": movies[:3]},
    )
