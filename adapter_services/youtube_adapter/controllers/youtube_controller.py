import os
from typing import Optional
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from shared.common.response import create_response
from shared.common.http_utils import make_request

class YoutubeSettings(BaseModel):
    youtube_search_url: str = "https://www.googleapis.com/youtube/v3/search"
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")

def get_settings():
    """Dependency injection for YouTube configuration"""
    return YoutubeSettings()


async def search_youtube(
    query: str = Query(
        ..., 
        description="Search query for finding relevant YouTube video",
        examples=["Titanic movie trailer 1997"],
        min_length=3
    ), 
    settings: YoutubeSettings = Depends(get_settings)
) -> JSONResponse:
    """
    Search for a video on YouTube and return the video ID or embed URL.
    """
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "key": settings.youtube_api_key,
    }

    try:
        result = make_request(settings.youtube_search_url, params=params)

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
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="YouTube service is temporarily unavailable"
        )
    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to YouTube API timed out"
        )
    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to fetch video from YouTube API"
        )

