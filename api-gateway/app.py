import logging

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
import httpx

from models import Movie, DiscoverResponse, DiscoverResult, MovieRecommendations, MovieRecommended
from config import EndpointConfig, get_endpoint_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)


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
    payload = {
        "message": "API Gateway is up and running"
    }

    return payload

@app.get("/v1/movie", response_model=Movie, status_code=200)
async def movie(
        id: int = Query(...), 
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client), 
):
    try:
        response = await client.get(
                url=f"{endpoints.movieUrl}",
                params={
                        "tmdbID": id
                    }
        )

        response.raise_for_status()
        data = response.json()
        movie = Movie(**data)
        if movie.poster_path and movie.backdrop_path:
            movie.poster_path = endpoints.posterUrl + movie.poster_path
            movie.backdrop_path = endpoints.posterUrl + movie.backdrop_path

        return movie
    
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


@app.get("/v1/discover", response_model=DiscoverResponse, status_code=200)
async def discover(
        language: str = Query(
                default="en-US",
                pattern="^[a-z]{2}-[A-Z]{2}$",
                description="Language code like en-US"
            ),
    with_genres: str = Query(...),
    page: int = Query(default=1),
    endpoints: EndpointConfig = Depends(get_endpoint_config),
    client: httpx.AsyncClient = Depends(get_http_client),
):

    try:

        response = await client.get(
            url=endpoints.discoverUrl,
            params={
                "language": language,
                "with_genres": with_genres,
                "page": page,
            },
        )

        response.raise_for_status()
        data = response.json()
        discover = DiscoverResponse(**data) # Validation & Serialization  
        for movie in discover.results:
            movie.poster_path = endpoints.posterUrl + movie.poster_path
            movie.backdrop_path = endpoints.posterUrl + movie.backdrop_path

        return discover

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



@app.get("/v1/by-genres", response_model=MovieRecommendations)
async def by_genres(
        genres: str = Query(...), 
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    try: 
        response = await client.get(
                url=endpoints.vibeUrl,
                params={"genres": genres}
        )

        response.raise_for_status()
        data = response.json()
        recommended_movies = MovieRecommendations(**data)
        for movie in recommended_movies.movies:
            if movie.poster_path and movie.backdrop_path:
                movie.poster_path = endpoints.posterUrl + movie.poster_path
                movie.backdrop_path = endpoints.posterUrl + movie.backdrop_path

        return recommended_movies
    
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


@app.get("/v1/similar", response_model=MovieRecommendations)
async def similar(
        id: int = Query(...),
        endpoints: EndpointConfig = Depends(get_endpoint_config),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    pass




