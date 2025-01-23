import requests
from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

class Settings(BaseModel):
    """Configuration settings for Spotify adapter"""
    spotify_url: str = "https://api.spotify.com/v1/search"
    spotify_track_url: str = "https://api.spotify.com/v1/tracks"
    spotify_auth_url: str = "https://accounts.spotify.com/api/token"
    spotify_client_id: str = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

def create_response(status_code: int, message: str, data: Optional[Dict[str, Any]] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def make_request(url: str, headers: dict, params: dict) -> Dict[str, Any]:
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return create_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message="Spotify API rate limit exceeded"
            )
        elif e.response.status_code == 401:
            return create_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid Spotify API credentials"
            )
        return create_response(
            status_code=e.response.status_code,
            message=f"Spotify API error: {str(e)}"
        )
    except requests.exceptions.ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Spotify service is currently unavailable"
        )
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to Spotify API timed out"
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to connect to Spotify: {str(e)}"
        )

def get_spotify_access_token(settings: Settings) -> str:
    try:
        response = requests.post(
            settings.spotify_auth_url,
            data={"grant_type": "client_credentials"},
            auth=(settings.spotify_client_id, settings.spotify_client_secret),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        return create_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid Spotify API credentials"
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=f"Failed to obtain Spotify access token: {str(e)}"
        )

def search_playlist_on_spotify(playlist_name: str, access_token: str, settings: Settings) -> Optional[str]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": playlist_name,
        "type": "playlist",
        "limit": 1,
        "market": "US"
    }
    data = make_request(settings.spotify_url, headers, params)
    playlists = data.get("playlists", {}).get("items", [])
    return playlists[0]["id"] if playlists else None

async def get_playlist_info(
    playlist_name: str = Query(..., description="Name of the playlist to search"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    try:
        access_token = get_spotify_access_token(settings)
        playlist_id = search_playlist_on_spotify(playlist_name, access_token, settings)
        if not playlist_id:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="No playlist found"
            )
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        playlist_data = response.json()
        
        playlist_info = {
            "spotify_url": playlist_data.get("external_urls", {}).get("spotify"),
            "cover_url": playlist_data.get("images", [{}])[0].get("url"),
            "name": playlist_data.get("name")
        }
        
        if not all(playlist_info.values()):
            return create_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Incomplete playlist data"
            )
            
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Playlist found successfully",
            data=playlist_info
        )
    except HTTPException as e:
        return create_response(
            status_code=e.status_code,
            message=str(e.detail)
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error"
        )

async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Spotify API adapter is up and running!"
    )