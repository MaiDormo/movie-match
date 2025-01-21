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
        content.update(data)
    return JSONResponse(content=content, status_code=status_code)

def make_request(url: str, headers: dict, params: dict) -> dict:
    """Make request to Spotify API with error handling"""
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Spotify API error: {str(e)}"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Spotify: {str(e)}"
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
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to obtain Spotify access token: {str(e)}"
        )

def search_song_on_spotify(song_name: str, access_token: str, settings: Settings) -> Optional[str]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": song_name,
        "type": "track",
        "limit": 1,
        "market": "US"
    }
    data = make_request(settings.spotify_url, headers, params)
    tracks = data.get("tracks", {}).get("items", [])
    return tracks[0]["id"] if tracks else None

def get_track_preview_url(track_id: str, access_token: str, settings: Settings) -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{settings.spotify_track_url}/{track_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    track_data = response.json()
    preview_url = track_data.get("preview_url")
    if not preview_url:
        raise ValueError(f"Preview for track ID {track_id} not available.")
    return preview_url

def get_track_details(track_id: str, access_token: str, settings: Settings) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{settings.spotify_track_url}/{track_id}"
    params = {"market": "US"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    track_data = response.json()
    return {
        "song_name": track_data.get("name"),
        "artist": track_data["artists"][0]["name"],
        "album": track_data["album"]["name"],
        "preview_url": track_data.get("preview_url"),
        "spotify_url": track_data["external_urls"]["spotify"],
        "track_id": track_data["id"],
        "popularity": track_data.get("popularity"),
        "duration_ms": track_data.get("duration_ms"),
        "explicit": track_data.get("explicit"),
        "release_date": track_data["album"].get("release_date")
    }

def get_preview_from_embed(track_id: str) -> Optional[str]:
    embed_url = f"https://open.spotify.com/embed/track/{track_id}"
    response = requests.get(embed_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    resource_element = soup.find(id="resource")
    if resource_element:
        track_details = resource_element.get('data-resource')
        return track_details.get("preview_url")
    return None

async def get_song(
    song_name: str = Query(..., description="Name of the song to search"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    try:
        access_token = get_spotify_access_token(settings)
        track_id = search_song_on_spotify(song_name, access_token, settings)
        if not track_id:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND, 
                message="No track found"
            )
        track_details = get_track_details(track_id, access_token, settings)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Track found successfully",
            data=track_details
        )
    except HTTPException as e:
        return create_response(
            status_code=e.status_code,
            message=str(e.detail)
        )
    except ValueError as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error"
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

def get_playlist_url(playlist_id: str, access_token: str, settings: Settings) -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    playlist_data = response.json()
    return playlist_data["external_urls"]["spotify"]

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

def get_playlist_tracks(playlist_id: str, access_token: str, settings: Settings) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"market": "US"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    track_data = response.json()
    tracks = []
    for track_item in track_data.get("items", [])[:10]:
        track = track_item["track"]
        tracks.append({
            "song_name": track["name"],
            "track_id": track["id"],
            "preview_url": track.get("preview_url"),
        })
    return tracks

async def get_playlist(
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
        playlist_url = get_playlist_url(playlist_id, access_token, settings)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Playlist found successfully",
            data={"playlist_url": playlist_url}
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