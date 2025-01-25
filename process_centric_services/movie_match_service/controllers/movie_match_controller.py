from fastapi import Depends, status, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel
import requests

# Constants
class Settings(BaseModel):
    MOVIE_DETAILS_URL: str = "http://movie-details-service:5000/api/v1/movie_details"
    MOVIE_SEARCH_GET_GENRES_URL: str = "http://movie-search-service:5000/api/v1/user_genres" 
    MOVIE_SEARCH_SET_GENRES_URL: str = "http://movie-search-service:5000/api/v1/update_user_genres"
    MOVIE_SEARCH_BY_TEXT_URL: str = "http://movie-search-service:5000/api/v1/movie_search_text"
    MOVIE_SEARCH_BY_GENRE_URL: str = "http://movie-search-service:5000/api/v1/movie_search_genre"

def get_settings():
    return Settings()

def create_response(
    status_code: int, 
    message: str, 
    data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def handle_service_request(method: str, url: str, **kwargs) -> Dict:
    """Handle external service requests with standardized error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        data = response.json()
        
        # Check if the response itself indicates an error
        if isinstance(data, dict) and data.get('status') == 'error':
            return create_response(
                status_code=data.get('code', response.status_code),
                message=data.get('message', 'Service error occurred'),
                data=data.get('data')
            )
            
        return data

    except requests.exceptions.HTTPError as http_err:
        try:
            error_data = response.json()
            return create_response(
                status_code=response.status_code,
                message=error_data.get('message', str(http_err)),
                data=error_data.get('data')
            )
        except ValueError:
            return create_response(
                status_code=response.status_code,
                message=str(http_err)
            )

    except requests.exceptions.ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Service is temporarily unavailable. Please try again later."
        )
        
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request timed out. Please try again."
        )
        
    except requests.exceptions.RequestException as req_err:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Service request failed: {str(req_err)}"
        )

    except ValueError as val_err:
        return create_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            message=f"Invalid response format from service: {str(val_err)}"
        )

async def fetch_data_from_service(
    url: str, 
    params: Optional[Dict[str, Any]] = None, 
    method: str = "get",
    json: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    try:
        response_data = handle_service_request(method, url, params=params, json=json)
        
        if isinstance(response_data, JSONResponse):
            return response_data
            
        if not isinstance(response_data, dict):
            return create_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message="Invalid response format from service"
            )

        if response_data.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=response_data.get("message", "Service request failed"),
                data=response_data.get("data")
            )
            
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Success",
            data=response_data.get("data")
        )
        
    except requests.RequestException as e:
        return create_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message=f"Service request failed: {str(e)}"
        )
        
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message=f"Internal server error: {str(e)}"
        )

# API endpoints with improved error handling
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Movie Match Service is up and running!"
    )

async def get_movie_details(id: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Fetch movie details by ID."""
    return await fetch_data_from_service(settings.MOVIE_DETAILS_URL, {"movie_id": id})

async def get_user_genres(user_id: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Fetch user genres based on user ID."""
    return await fetch_data_from_service(settings.MOVIE_SEARCH_GET_GENRES_URL, {"user_id": user_id})

async def update_user_genres(user_id: str, preferences: list[int], settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Update user genres preferences based on user ID."""
    return await fetch_data_from_service(
        f"{settings.MOVIE_SEARCH_SET_GENRES_URL}?id={user_id}", 
        json=preferences, 
        method="put"
    )

async def get_movie_search_by_text(query: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Search for movies based on a text query."""
    return await fetch_data_from_service(settings.MOVIE_SEARCH_BY_TEXT_URL, {"query": query})

async def get_genre_movie_search_by_url(with_genres: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Search for movies based on genres."""
    params = {
        "language": "en-EN",
        "with_genres": with_genres,
        "vote_avg_gt": 6.5,
        "sort_by": "popularity.desc"
    }
    return await fetch_data_from_service(settings.MOVIE_SEARCH_BY_GENRE_URL, params)