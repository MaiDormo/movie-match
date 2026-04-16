import base64
import os
from typing import Optional
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from shared.common.response import create_response
from shared.common.http_utils import make_request


class SpotifySettings(BaseModel):
    search_url: str = "https://api.spotify.com/v1/search"
    playlist_url: str = "https://api.spotify.com/v1/playlists"
    auth_url: str = "https://accounts.spotify.com/api/token"
    client_id: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_settings() -> SpotifySettings:
    return SpotifySettings()


def get_spotify_access_token(settings: SpotifySettings) -> Optional[str]:
    """Get Spotify OAuth access token using Client Credentials flow."""
    try:
        auth_string = base64.b64encode(
            f"{settings.client_id}:{settings.client_secret}".encode()
        ).decode()

        response_data = make_request(
            url=settings.auth_url,
            method="post",
            data={"grant_type": "client_credentials"},
            headers={
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return response_data.get("access_token")
    except (HTTPError, ConnectionError, Timeout, RequestException):
        return None


def search_playlist_on_spotify(
    playlist_name: str, access_token: str, settings: SpotifySettings
) -> Optional[str]:
    """Search for a playlist and return its ID."""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "q": playlist_name,
            "type": "playlist",
            "limit": 1,
            "offset": 0,
            "market": "US",
        }
        data = make_request(settings.search_url, headers=headers, params=params)
        playlists = data.get("playlists", {}).get("items", [])
        return playlists[0]["id"] if playlists else None
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        return None


async def get_playlist_info(
    playlist_name: str = Query(..., description="Name of the playlist to search"),
    settings: SpotifySettings = Depends(get_settings),
) -> JSONResponse:
    """Get playlist information from Spotify"""
    try:
        access_token = get_spotify_access_token(settings)
        if not access_token:
            return create_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Failed to authenticate with Spotify",
            )

        playlist_id = search_playlist_on_spotify(playlist_name, access_token, settings)
        if not playlist_id:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND, message="No playlist found"
            )

        headers = {"Authorization": f"Bearer {access_token}"}
        playlist_url = f"{settings.playlist_url}/{playlist_id}"
        playlist_data = make_request(playlist_url, headers=headers)

        playlist_info = {
            "spotify_url": playlist_data.get("external_urls", {}).get("spotify"),
            "cover_url": playlist_data.get("images", [{}])[0].get("url"),
            "name": playlist_data.get("name"),
        }

        if not all(playlist_info.values()):
            return create_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Incomplete playlist data",
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Playlist found successfully",
            data=playlist_info,
        )

    except HTTPError as e:
        if e.response.status_code == 429:
            return create_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message="Spotify API rate limit exceeded",
            )
        elif e.response.status_code == 401:
            return create_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid Spotify API credentials",
            )
        return create_response(
            status_code=e.response.status_code, message=f"Spotify API error: {str(e)}"
        )
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Spotify service is currently unavailable",
        )
    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to Spotify API timed out",
        )
    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to connect to Spotify: {str(e)}",
        )
    except Exception:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
