import os
from pydantic import BaseModel


class Settings(BaseModel):
    tmdb_api_key: str | None = os.getenv("TMDB_API_KEY")
    tmdb_base_url: str = "https://api.themoviedb.org/3/movie/"
    tmdb_language: str = "en-US"

    youtube_api_key: str | None = os.getenv("YOUTUBE_API_KEY")
    youtube_search_url: str = "https://www.googleapis.com/youtube/v3/search"

    spotify_client_id: str | None = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret: str | None = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_auth_url: str = "https://accounts.spotify.com/api/token"
    spotify_search_url: str = "https://api.spotify.com/v1/search"
    spotify_playlist_url: str = "https://api.spotify.com/v1/playlists"

    cerebras_api_key: str | None = os.getenv("CEREBRAS_API_KEY")
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "llama3.1-8b"

    streaming_api_key: str | None = os.getenv("STREAMING_AVAILABILITY_API_KEY")
    streaming_api_host: str = "streaming-availability.p.rapidapi.com"
    streaming_api_url: str = "https://streaming-availability.p.rapidapi.com/shows"
    streaming_country: str = "us"

    timeout: float = 10.0


def get_settings() -> Settings:
    return Settings()
