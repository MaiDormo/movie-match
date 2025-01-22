import asyncio
from functools import partial
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx

router = APIRouter()

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
    """
    Factory function for Settings dependency injection.
    
    Returns:
        Settings: Configuration object with service URLs
    """
    return Settings()

async def fetch_data(url: str, params: dict = None) -> Dict[str, Any]:
    """
    Generic function to fetch data from external services.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
async def fetch_data(url: str, params: dict = None, settings: Settings = None) -> Dict[str, Any] | None:
    """Enhanced fetch function with retry logic"""
    for attempt in range(settings.max_retries):
        try:
            async with httpx.AsyncClient(timeout=settings.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == settings.max_retries - 1:
                raise
            await asyncio.sleep(settings.retry_delay)
    return None
    
def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """
    Create a standardized API response.
    
    Args:
        status_code (int): HTTP status code
        message (str): Response message
        data (Dict[str, Any], optional): Response payload. Defaults to None.
    
    Returns:
        JSONResponse: Formatted API response
    """
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def get_movie_details(movie_id: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Aggregate movie details with parallel fetching and better error handling"""
    try:
        # First fetch OMDB data since others depend on it
        omdb_data = await fetch_data(settings.omdb_url, {"id": movie_id}, settings)
        if not omdb_data:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="OMDB service unavailable"
            )

        # Parallel fetch remaining data
        fetch = partial(fetch_data, settings=settings)
        tasks = [
            fetch(settings.youtube_url, {"query": f"{omdb_data['Title']} trailer"}),
            fetch(settings.spotify_url, {"playlist_name": omdb_data['Title']}),
            fetch(settings.streaming_url, {"imdb_id": movie_id, "country": "it"}),
            fetch(settings.trivia_url, {"movie_title": omdb_data['Title']})
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        service_data = {
            "omdb": omdb_data,
            "youtube": results[0] if not isinstance(results[0], Exception) else None,
            "spotify": results[1] if not isinstance(results[1], Exception) else None,
            "streaming": results[2] if not isinstance(results[2], Exception) else None,
            "trivia": results[3] if not isinstance(results[3], Exception) else None
        }

        # Check if at least some services responded
        if all(v is None for v in service_data.values()):
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="All services are currently unavailable"
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movie details retrieved partially" if None in service_data.values() else "Movie details retrieved successfully",
            data={"movie_details": service_data}
        )

    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data={"error": str(e)}
        )
    

async def health_check():
    return create_response(
        status_code=200,
        message="Movie Details Service is up and running!"
    )