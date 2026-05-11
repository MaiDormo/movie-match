import asyncio
import base64
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
import httpx

from config import Settings, get_settings
from models import EnrichmentResponse, YouTubeResult, SpotifyResult, StreamingResult, StreamingService

logger = logging.getLogger("enrichment-svc")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(title="Enrichment Service", lifespan=lifespan)


async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


async def fetch_json(
    client: httpx.AsyncClient,
    url: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    method: str = "GET",
    data: Optional[dict] = None,
) -> dict:
    """Helper to fetch JSON from upstream services."""
    try:
        if method.upper() == "GET":
            response = await client.request(method, url, params=params, headers=headers)
        else:
            response = await client.request(method, url, params=params, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.warning("Request failed for %s: %s", url, e)
        return {}
    except httpx.HTTPStatusError as e:
        logger.warning("HTTP error from %s: %s", url, e)
        return {}


async def _fetch_youtube(client: httpx.AsyncClient, settings: Settings, title: str) -> Optional[YouTubeResult]:
    if not (settings.youtube_api_key and title):
        return None
        
    youtube_data = await fetch_json(
        client,
        settings.youtube_search_url,
        params={
            "part": "snippet",
            "q": f"{title} official trailer",
            "type": "video",
            "maxResults": 1,
            "key": settings.youtube_api_key,
        },
    )

    if youtube_data.get("items"):
        video_id = youtube_data["items"][0]["id"]["videoId"]
        return YouTubeResult(
            video_id=video_id,
            embed_url=f"https://www.youtube.com/embed/{video_id}",
        )
    return None


async def _fetch_spotify(client: httpx.AsyncClient, settings: Settings, title: str) -> Optional[SpotifyResult]:
    if not (settings.spotify_client_id and settings.spotify_client_secret and title):
        return None
        
    auth_string = base64.b64encode(
        f"{settings.spotify_client_id}:{settings.spotify_client_secret}".encode()
    ).decode()
    
    token_data = await fetch_json(
        client,
        settings.spotify_auth_url,
        method="POST",
        data={"grant_type": "client_credentials"},
        headers={
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    
    access_token = token_data.get("access_token")
    if not access_token:
        return None
        
    playlist_search = await fetch_json(
        client,
        settings.spotify_search_url,
        params={
            "q": f"{title} soundtrack",
            "type": "playlist",
            "limit": 1,
            "offset": 0,
            "market": "US",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    items = playlist_search.get("playlists", {})
    if items is None:
        items = {}
    items_list = items.get("items", [])
    if not items_list:
        return None
        
    playlist_id = items_list[0].get("id") if isinstance(items_list[0], dict) else None
    if not playlist_id:
        return None
        
    playlist_data = await fetch_json(
        client,
        f"{settings.spotify_playlist_url}/{playlist_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    return SpotifyResult(
        spotify_url=playlist_data.get("external_urls", {}).get("spotify"),
        cover_url=(playlist_data.get("images") or [{}])[0].get("url"),
        name=playlist_data.get("name"),
    )


async def _fetch_streaming(client: httpx.AsyncClient, settings: Settings, imdb_id: str) -> Optional[StreamingResult]:
    if not (imdb_id and settings.streaming_api_key):
        return None
        
    streaming_data = await fetch_json(
        client,
        f"{settings.streaming_api_url}/{imdb_id}",
        params={"country": settings.streaming_country},
        headers={
            "x-rapidapi-key": settings.streaming_api_key,
            "x-rapidapi-host": settings.streaming_api_host,
        },
    )
    
    options = streaming_data.get("streamingOptions", {}).get(settings.streaming_country, [])
    if options:
        services = []
        seen = set()
        for opt in options:
            name = opt.get("service", {}).get("name")
            if not name or name in seen:
                continue
            seen.add(name)
            services.append(
                StreamingService(
                    service_name=name,
                    logo=opt.get("service", {}).get("imageSet", {}).get("lightThemeImage"),
                    link=opt.get("link"),
                )
            )
        if services:
            return StreamingResult(services=services)
    return None


@app.get("/health", status_code=200)
async def health():
    return {"status": "ok", "message": "Enrichment Service is up and running"}


@app.get("/v1/enrich", response_model=EnrichmentResponse, status_code=200)
async def enrich_movie(
        tmdb_id: int = Query(..., description="TMDB movie ID"),
        client: httpx.AsyncClient = Depends(get_http_client),
        settings: Settings = Depends(get_settings),
):
    """Enrich movie data with YouTube trailer, Spotify soundtrack, and streaming availability."""

    if not settings.tmdb_api_key:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY is not configured")

    tmdb_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.tmdb_api_key}",
    }

    # Step 1: We must fetch TMDB first because we need the 'title' and 'imdb_id' 
    # to query the downstream services
    tmdb_data = await fetch_json(
        client,
        f"{settings.tmdb_base_url}{tmdb_id}",
        params={"language": settings.tmdb_language},
        headers=tmdb_headers,
    )

    title = tmdb_data.get("title", "")
    imdb_id = tmdb_data.get("imdb_id", "")

    # Step 2: Run all enrichment fetching concurrently
    youtube_task = _fetch_youtube(client, settings, title)
    spotify_task = _fetch_spotify(client, settings, title)
    streaming_task = _fetch_streaming(client, settings, imdb_id)

    results = await asyncio.gather(youtube_task, spotify_task, streaming_task)
    youtube, spotify, streaming = results

    return EnrichmentResponse(
        tmdb_id=tmdb_id,
        title=title,
        imdb_id=imdb_id,
        poster_path=tmdb_data.get("poster_path"),
        release_date=tmdb_data.get("release_date"),
        runtime=tmdb_data.get("runtime"),
        genres=tmdb_data.get("genres"),
        overview=tmdb_data.get("overview"),
        vote_average=tmdb_data.get("vote_average"),
        youtube=youtube,
        spotify=spotify,
        streaming=streaming,
    )
