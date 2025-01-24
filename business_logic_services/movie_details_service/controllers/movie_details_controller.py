import asyncio
from functools import partial
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import requests

class Settings(BaseModel):
    """Configuration settings for external service endpoints."""
    omdb_url: str = "http://omdb-adapter:5000/api/v1/find"
    youtube_url: str = "http://youtube-adapter:5000/api/v1/get_video"
    spotify_url: str = "http://spotify-adapter:5000/api/v1/search_playlist"
    streaming_url: str = "http://streaming-availability-adapter:5000/api/v1/avail"
    trivia_url: str = "http://groq-adapter:5000/api/v1/get_trivia"
    timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0

def get_settings() -> Settings:
    """Factory function for Settings dependency injection."""
    return Settings()

async def fetch_data(url: str, params: dict = None, settings: Settings = None) -> Dict[str, Any]:
    """Generic function to fetch data from external services with retry logic."""
    for attempt in range(settings.max_retries):
        try:
            async with httpx.AsyncClient(timeout=settings.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                return create_response(
                    status_code=e.response.status_code,
                    message=error_data.get('message', str(e)),
                    data=error_data.get('data')
                )
            except ValueError:
                return create_response(
                    status_code=e.response.status_code,
                    message=str(e)
                )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt == settings.max_retries - 1:
                return create_response(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    message="Service temporarily unavailable"
                )
            await asyncio.sleep(settings.retry_delay)
    return None

async def fetch_movie_services(omdb_data: dict, movie_id: str, settings: Settings) -> list:
    """Fetch data from auxiliary movie services in parallel."""
    fetch = partial(fetch_data, settings=settings)
    tasks = [
        fetch(settings.youtube_url, {"query": f"{omdb_data['Title']} trailer"}),
        fetch(settings.spotify_url, {"playlist_name": omdb_data['Title']}),
        fetch(settings.streaming_url, {"imdb_id": movie_id, "country": "it"}),
        fetch(settings.trivia_url, {"movie_title": omdb_data['Title']})
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)

def process_service_results(omdb_data: dict, results: list) -> dict:
    """Process and combine results from all movie services."""
    return {
        "omdb": omdb_data,
        "youtube": results[0] if not isinstance(results[0], Exception) else None,
        "spotify": results[1] if not isinstance(results[1], Exception) else None,
        "streaming": results[2] if not isinstance(results[2], Exception) else None,
        "trivia": results[3] if not isinstance(results[3], Exception) else None
    }

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response."""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def get_movie_details(movie_id: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Aggregate movie details with parallel fetching and error handling."""
    try:
        # Get base movie data
        omdb_response = await fetch_data(settings.omdb_url, {"id": movie_id}, settings)
        
        # Handle JSONResponse type responses (error cases)
        if isinstance(omdb_response, JSONResponse):
            return omdb_response
            
        if not omdb_response:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="OMDB service unavailable"
            )

        omdb_data = omdb_response["data"]
        
        # Rest of the function remains the same
        results = await fetch_movie_services(omdb_data, movie_id, settings)
        service_data = process_service_results(omdb_data, results)
        
        if all(v is None for v in service_data.values()):
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="All services are currently unavailable"
            )

        success = not any(v is None for v in service_data.values())
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movie details retrieved successfully" if success else "Movie details retrieved partially",
            data={"movie_details": service_data}
        )

    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data={"error": str(e)}
        )

async def health_check():
    """Health check endpoint."""
    return create_response(
        status_code=200,
        message="Movie Details Service is up and running!"
    )