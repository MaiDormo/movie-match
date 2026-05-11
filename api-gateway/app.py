import logging

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
import httpx

from models import Movie, DiscoverResponse, MovieRecommendations, VibeList, EnrichmentResponse
from config import EndpointConfig, get_endpoint_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(title="MovieMatch API Gateway", lifespan=lifespan)


async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("app")


@app.get("/health", status_code=200)
async def health():
    return {"status": "ok", "message": "API Gateway is up and running"}


# ===== Vibes =====

@app.get("/v1/vibes", response_model=VibeList, status_code=200)
async def get_vibes(
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get list of available vibes from recommendation service."""
    try:
        response = await client.get(f"{endpoints.recommendationUrl}/v1/vibes")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail="Recommendation service unavailable")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail="Failed to fetch vibes")


# ===== Recommendations =====

@app.get("/v1/recommendations/by-vibe", response_model=MovieRecommendations, status_code=200)
async def recommend_by_vibe(
        vibes: str = Query(..., description="Comma-separated vibe names"),
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get movie recommendations based on vibes."""
    try:
        response = await client.get(
            f"{endpoints.recommendationUrl}/v1/recommend/by-vibe",
            params={"vibes": vibes}
        )
        response.raise_for_status()
        return response.json()
    except ValidationError as e:
        logger.critical("Response schema mismatch: %s", e)
        raise HTTPException(status_code=502, detail="Unexpected data from upstream")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Recommendation service unavailable")
    except httpx.HTTPStatusError as e:
        logger.warning("Recommendation svc returned %s", e.response.status_code)
        raise HTTPException(status_code=502, detail="Upstream service error")


@app.get("/v1/recommendations/by-genres", response_model=MovieRecommendations, status_code=200)
async def recommend_by_genres(
        genres: str = Query(..., description="Comma-separated genre IDs"),
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get movie recommendations based on genre IDs."""
    try:
        response = await client.get(
            f"{endpoints.recommendationUrl}/v1/recommend/by-genres",
            params={"genres": genres}
        )
        response.raise_for_status()
        return response.json()
    except ValidationError as e:
        logger.critical("Response schema mismatch: %s", e)
        raise HTTPException(status_code=502, detail="Unexpected data from upstream")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Recommendation service unavailable")
    except httpx.HTTPStatusError as e:
        logger.warning("Recommendation svc returned %s", e.response.status_code)
        raise HTTPException(status_code=502, detail="Upstream service error")


# ===== Movie Core =====

@app.get("/v1/movie/{tmdb_id}", response_model=Movie, status_code=200)
async def get_movie(
        tmdb_id: int,
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get movie details by TMDB ID."""
    try:
        response = await client.get(
            f"{endpoints.movieCoreUrl}/v1/movie",
            params={"tmdbID": tmdb_id}
        )
        response.raise_for_status()
        data = response.json()

        return Movie(**data)
    except ValidationError as e:
        logger.critical("TMDB Response schema mismatch: %s", e)
        raise HTTPException(status_code=502, detail="Unexpected data from upstream")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Movie core service unavailable")
    except httpx.HTTPStatusError as e:
        logger.warning("TMDB returned %s", e.response.status_code)
        raise HTTPException(status_code=502, detail="Upstream service error")


@app.get("/v1/discover", response_model=DiscoverResponse, status_code=200)
async def discover_movies(
        with_genres: str = Query(..., description="Comma-separated genre IDs"),
        language: str = Query(default="en-US", description="Language code like en-US"),
        page: int = Query(default=1),
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Discover movies by genre."""
    try:
        response = await client.get(
            f"{endpoints.movieCoreUrl}/v1/discover",
            params={"language": language, "with_genres": with_genres, "page": page}
        )
        response.raise_for_status()
        data = response.json()
        return DiscoverResponse(**data)
    except ValidationError as e:
        logger.critical("TMDB Response schema mismatch: %s", e)
        raise HTTPException(status_code=502, detail="Unexpected data from upstream")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Movie core service unavailable")
    except httpx.HTTPStatusError as e:
        logger.warning("TMDB returned %s", e.response.status_code)
        raise HTTPException(status_code=502, detail="Upstream service error")


# ===== Enrichment =====

@app.get("/v1/movie/{tmdb_id}/enrichment", response_model=EnrichmentResponse, status_code=200)
async def get_enrichment(
        tmdb_id: int,
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get enriched movie data (YouTube, Spotify, streaming)."""
    try:
        response = await client.get(
            f"{endpoints.enrichmentUrl}/v1/enrich",
            params={"tmdb_id": tmdb_id}
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Enrichment service unavailable")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Enrichment service error")


