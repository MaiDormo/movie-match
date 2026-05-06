import logging
import re

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from contextlib import asynccontextmanager
import httpx

from config import TMDBConfig, getTMDBConfig
from models import TMDBDiscoverResponse, TMDBMovie 


# This is used to tie the app with the client avoiding creating too many clients
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    try:
        yield
    finally:
        await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

# Dependency Injection trick
async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


# TODO After builing frontend tighten the CORS Origins

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
)

logger = logging.getLogger("app")

@app.get("/health", status_code=200)
async def health():
    payload = {
        "message": "Movie Core is up and running!"
    }
    return payload

@app.get("/v1/movie", status_code=200, response_model=TMDBMovie)
async def getMovieDetails(
        tmdbID: int = Query(..., ge=1),
        language: str = Query(
                default="en-US",
                pattern="^[a-z]{2}-[A-Z]{2}$",
                description="Language code like en-US"
            ),
        config: TMDBConfig = Depends(getTMDBConfig),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {config.tmdbKey}",
    }

    try:
        response = await client.get(
            url=f"{config.tmdbMovieDetails}{tmdbID}",
            headers=headers,
            params={"language": language},
        )
        
        response.raise_for_status()
        data = response.json()
        return TMDBMovie(**data)
    
    except ValidationError as e:
        logger.critical("TMDB Response schema mismatch: %s", e)
        raise HTTPException(
            status_code=502,
            detail="Unexpected Data from upstream"
        )
    except httpx.RequestError as e:
        raise HTTPException(
                status_code=502,
                detail="TMDB Request Failed",
        )
    except httpx.HTTPStatusError as e:
        logger.warning("TMDB returned %s: %s", e.response.status_code, e.response.text[:200])
        raise HTTPException(
                status_code=502,
                detail="Upstream Service Error",
        ) 
@app.get("/v1/discover", status_code=200, response_model=TMDBDiscoverResponse)
async def getMovieDiscovery(
    language: str = Query(
                ...,
                pattern="^[a-z]{2}-[A-Z]{2}$",
                description="Language code like en-US"
            ),
    with_genres: str = Query(...),
    page: int = Query(...),
    config: TMDBConfig = Depends(getTMDBConfig),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {config.tmdbKey}"
    }

    try:

        response = await client.get(
            url=config.tmdbMovieDiscover,
            headers=headers,
            params={
                "language": language,
                "with_genres": with_genres,
                "page": page,
                "vote_count.gte": 100,
            },
        )

        response.raise_for_status()
        data = response.json()
        return TMDBDiscoverResponse(**data) # Validation & Serialization  
    except ValidationError as e:
        logger.critical("TMDB Response schema mismatch: %s", e)
        raise HTTPException(
                status_code=502,
                detail="Unexpected Data from upstream"
            )
    except httpx.RequestError as e:
        raise HTTPException(
                status_code=502,
                detail="TMDB Request Failed",
            )
    except httpx.HTTPStatusError as e:
        logger.warning("TMDB returned %s: %s", e.response.status_code, e.response.text[:200])
        raise HTTPException(
                status_code=502,
                detail="Upstream Service Error",
            )
