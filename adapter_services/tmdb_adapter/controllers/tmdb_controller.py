from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
import requests
import re

class Settings(BaseModel):
    tmdb_url: str = "https://api.themoviedb.org/3/movie/"
    tmdb_discover_movie: str = "https://api.themoviedb.org/3/discover/movie"
    tmdb_api_key: str = os.getenv("TMDB_API_KEY")
    external_source: str = "imdb_id"

def get_settings():
    return Settings()

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def make_request(url: str, headers: dict, params: dict) -> dict:
    """Make HTTP request with error handling."""
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=str(e)
        )
    except requests.exceptions.ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="TMDB API is currently unavailable"
        )
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to TMDB API timed out"
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error callinng TMDB API",
            data={"error": str(e)}
        )

def is_valid_language(language: str) -> bool:
    """Validate language format."""
    pattern = re.compile(r'^[a-z]{2}-[A-Z]{2}$')
    return bool(pattern.match(language))

def filter_data(tmdb_data: dict) -> dict:
    """Filter and extract relevant movie data."""
    if not tmdb_data.get("imdb_id"):
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No IMDB_ID found for {tmdb_data.get('id')}"
        )
    return tmdb_data["imdb_id"]

async def get_movie_imdb_id(
    id: int = Query(...), 
    language: str = Query(...), 
    settings: Settings = Depends(get_settings)
):
    if not id or not language:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Title and language are required"
        )
    
    if not is_valid_language(language):
        raise create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language format. Expected format: en-US, de-DE, it-IT, etc."
        )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.tmdb_api_key}"
    }
    params = {
        "language": language,
    }

    try:
        response = make_request(settings.tmdb_url + f"{id}", headers, params)
        
        if isinstance(response,JSONResponse):
            return response
        
        imdb_id = filter_data(response)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="IMDB ID retrieved successfully",
            data= {"imdb_id": imdb_id}
        )
    except HTTPException as e:
        return create_response(
            status_code=e.status_code,
            message=str(e.detail)
        )
    
async def get_movie(
    id: int = Query(...), 
    language: str = Query(...), 
    settings: Settings = Depends(get_settings)
):
    if not id or not language:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Title and language are required"
        )
    
    if not is_valid_language(language):
        raise create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language format. Expected format: en-US, de-DE, it-IT, etc."
        )

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.tmdb_api_key}"
    }
    params = {
        "language": language,
    }

    try:
        response = make_request(settings.tmdb_url + f"{id}", headers, params)
        
        if isinstance(response,JSONResponse):
            return response

        return create_response(
            status_code=status.HTTP_200_OK,
            message="IMDB ID retrieved successfully",
            data= {"movie_list": response}
        )
    
    except HTTPException as e:
        return create_response(
            status_code=e.status_code,
            message=str(e.detail)
        )

async def discover_movies(
    language: str = Query(...), 
    with_genres: str = Query(...), 
    vote_avg_gt: float = Query(...), 
    sort_by: str = Query(default="popularity.desc", description="Sort results by this value"),
    settings: Settings = Depends(get_settings)
):
    # Validate language format
    if not is_valid_language(language):
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid language format. Expected format: en-US, de-DE, it-IT, etc.",
        )
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.tmdb_api_key}"
    }

    params = {
        "language": language,
        "with_genres": with_genres,
        "vote_average.gte": vote_avg_gt,
        "sort_by": sort_by,
        "include_adult": False,
        "include_video": False,
        "page": 1,
        "vote_count.gte": 100 #Added mininum vote count to ensure rating reliability
    }

    try:
        movies = make_request(settings.tmdb_discover_movie, headers, params)

        if isinstance(movies,JSONResponse):
            return movies
        
        if not movies.get("results"):
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="No movies found matching the criteria",
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies retrieved successfully",
            data={
                "total_results": movies["total_results"],
                "total_pages": movies["total_pages"],
                "results": movies["results"]
            }
        )
    except HTTPException as e:
        return create_response(
            status_code=e.status_code,
            message="HTTP error occurred",
            data={"error": str(e.detail)},
        )
    except requests.exceptions.ConnectionError as e:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Connection error occurred",
            data={"error": str(e)},
        )
    except requests.exceptions.Timeout as e:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request timed out",
            data={"error": str(e)},
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while calling the TMDB API",
            data={"error": str(e)},
        )

async def health_check():
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="TMDB API Adapter is up and running!"
    )