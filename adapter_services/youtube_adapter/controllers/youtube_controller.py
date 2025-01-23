from typing import Any, Dict, Optional
from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
import os
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

class Settings(BaseModel):
    youtube_search_url: str = "https://www.googleapis.com/youtube/v3/search"
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY")

def get_settings():
    """Dependency injection for YouTube configuration"""
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

def make_request(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=200,
        message="YOUTUBE API Adapter is up and running!"
    )

async def search_youtube(
    query: str = Query(
        ..., 
        description="Search query for finding relevant YouTube video",
        example="Titanic movie trailer 1997",
        min_length=3
    ), 
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """
    Cerca un video su YouTube utilizzando una stringa di query e restituisce l'ID del video o l'URL embed.
    """
    
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "key": settings.youtube_api_key,
    }

    try:
        result = make_request(settings.youtube_search_url, params)

        if "items" not in result or len(result["items"]) == 0:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="No videos found for the provided query"
            )

        video_id = result["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/embed/{video_id}"
        
        return create_response(
            status_code=status.HTTP_200_OK,
            message="YouTube video retrieved successfully",
            data={
                "video_id": video_id,
                "embed_url": video_url
            }
        )

    except HTTPError as e:
        error_msg = f"HTTP error occurred: {str(e)}"
        if e.response.status_code == 401:
            error_msg = "Invalid YouTube API key"
        elif e.response.status_code == 429:
            error_msg = "YouTube API quota exceeded"
            
        return create_response(
            status_code=e.response.status_code,
            message=error_msg
        )
    except ConnectionError as e:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="YouTube service is temporarily unavailable",
            data={"error": str(e)}
        )
    except Timeout as e:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to YouTube API timed out",
            data={"error": str(e)}
        )
    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to fetch video from YouTube API",
            data={"error": str(e)}
        )

