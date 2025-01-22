from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import requests
from typing import Dict, Any
from functools import wraps

class Settings(BaseModel):
    """Configuration settings for OMDB adapter"""
    omdb_url: str = Field(default="http://www.omdbapi.com/", description="OMDB API base URL")
    omdb_api_key: str = Field(default=os.getenv("OMDB_API_KEY"), description="OMDB API key from environment")

def get_settings() -> Settings:
    """Get application settings"""
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

def handle_api_errors(func):
    """Decorator for handling API request errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"HTTP error occurred: {str(e)}"
            )
        except requests.exceptions.ConnectionError:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="OMDB API is currently unavailable"
            )
        except requests.exceptions.Timeout:
            return create_response(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                message="Request to OMDB API timed out"
            )
        except requests.exceptions.RequestException as e:
            return create_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Error calling OMDB API: {str(e)}"
            )
    return wrapper

def make_request(url: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Make HTTP request to OMDB API"""
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if 'Error' in data:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=data['Error']
        )
    return data

@handle_api_errors
async def get_movies(
    title: str = Query(..., description="Movie title to search for"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Search movies by title"""
    params = {
        "apikey": settings.omdb_api_key,
        "s": title,
        "type": "movie"
    }
    
    movies = make_request(settings.omdb_url, params)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Movies retrieved successfully",
        data=movies
    )

@handle_api_errors
async def get_movie_id(
    id: str = Query(..., description="IMDB movie ID"),
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """Get movie details by IMDB ID"""
    params = {
        "apikey": settings.omdb_api_key,
        "i": id,
    }
    
    return make_request(settings.omdb_url, params)

@handle_api_errors
async def get_movies_with_info(
    title: str = Query(..., description="Movie title to search for"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Search movies and include additional details"""
    params = {
        "apikey": settings.omdb_api_key,
        "s": title,
        "type": "movie"
    }
    
    # Get initial movie list
    movies = make_request(settings.omdb_url, params)
    
    if isinstance(movies, JSONResponse):
        return movies

    films_list = movies.get("Search", [])
    
    # Get detailed information for each movie
    detailed_movies = []
    for movie in films_list:
        movie_details = await get_movie_id(id=movie["imdbID"], settings=settings)
        detailed_movies.append({
            **movie,
            "Genre": movie_details.get("Genre", "N/A"),
            "imdbRating": movie_details.get("imdbRating", "N/A")
        })

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Movies retrieved successfully",
        data=detailed_movies
    )

async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="OMDB API Adapter is up and running!"
    )