import asyncio
from typing import Any, Dict
from fastapi import Depends, status, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx

class Settings(BaseModel):
    """Configuration settings for external service endpoints."""
    genres_url: str = "http://postgrest:3000/genres"
    preferences_url: str = "http://user-db-adapter:5000/api/v1/user"
    tmdb_url: str = "http://tmdb-adapter:5000/api/v1/discover-movies"
    tmdb_movie_url: str = "http://tmdb-adapter:5000/api/v1/movie"
    
    timeout: float = 15.0
    max_retries: int = 3
    retry_delay: float = 1.5

def get_settings() -> Settings:
    """
    Factory function for Settings dependency injection.
    
    Returns:
        Settings: Configuration object with service URLs
    """
    return Settings()

async def fetch_data(url: str, method: str = "GET", params: dict | None = None, settings: Settings | None = None) -> Dict[str, Any] | JSONResponse | None:
    """Generic function to fetch data from external services with retry logic."""
    if not settings:
        return None
    for attempt in range(settings.max_retries):
        try:
            async with httpx.AsyncClient(timeout=settings.timeout) as client:
                if method == "PUT":
                    response = await client.put(url, json=params)
                else:
                    response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                return create_response(
                    status_code=e.response.status_code,
                    message=error_data.get('message', str(e)),
                    data=error_data.get('data')
                )
            except ValueError:
                return create_response(
                    status_code=e.response.status_code,
                    message=str(e)
                )
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt == settings.max_retries - 1:
                return create_response(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    message="Service temporarily unavailable"
                )
            await asyncio.sleep(settings.retry_delay)
    return None
    
def create_response(status_code: int, message: str, data: Dict[str, Any] | None = None) -> JSONResponse:
    """
    Create a standardized API response.
    
    Args:
        status_code (int): HTTP status code
        message (str): Response message
        data (Dict[str, Any], optional): Response payload. Defaults to None.
    
    Returns:
        JSONResponse: Formatted API response
    """
    content: Dict[str, Any] = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def get_genre_movie_search(
    language: str = Query(...), 
    with_genres: str = Query(...), 
    vote_avg_gt: float = Query(...), 
    sort_by: str = Query(default="popularity.desc", description="Sort results by this value"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    try:
        # Ottieni la lista dei film da TMDB
        movie_list_data = await fetch_data(
            url=settings.tmdb_url,
            params={
                "language": language,
                "with_genres": with_genres,
                "vote_avg_gt": vote_avg_gt,
                "sort_by": sort_by
            },
            settings=settings
        )

        if isinstance(movie_list_data, JSONResponse):
            return movie_list_data
        
        if not isinstance(movie_list_data, dict):
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="Invalid response from TMDB service"
            )

        if movie_list_data.get("status") != "success":
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="TMDB service unavailable"
            )

        movies = movie_list_data.get("data", {}).get("movie_list", [])
        movie_details = []

        # Per ogni film, fai una chiamata all'endpoint per recuperare dettagli aggiuntivi
        for movie in movies:
            movie_id = movie["tmdbId"]
            try:
                details_response = await fetch_data(
                    url=settings.tmdb_movie_url,
                    params={"id": movie_id, "language": language},
                    settings=settings
                )

                if details_response and isinstance(details_response, dict) and details_response.get("status") == "success":
                    details = details_response["data"]["movie"]

                    # Crea un oggetto con i dati richiesti
                    processed_movie = {
                        "Title": details.get("Title", "N/A"),
                        "Year": details.get("Year", "N/A").split("-")[0],
                        "imdbID": details.get("imdbId", "N/A"),
                        "Poster": f"https://image.tmdb.org/t/p/original/{details.get('Poster', '')}",
                        "Genre": ", ".join([genre["name"] for genre in details.get("GenreIds", [])]),
                        "imdbRating": round(details.get("Rating", 0), 1)
                    }
                    movie_details.append(processed_movie)
            except Exception as e:
                # Logga eventuali errori per film specifici e continua
                print(f"Error fetching details for movie ID {movie_id}: {e}")

        # Ordina i film per valutazione
        movie_details.sort(key=lambda x: x["imdbRating"], reverse=True)

        # Risposta di successo con i dettagli dei film
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies retrieved successfully",
            data={"movie_list": movie_details}
        )

    except Exception as e:
        # Gestione degli errori generali
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data={"error": str(e)}
        )

async def health_check():
    return create_response(
        status_code=200,
        message="Movie Details Service is up and running!"
    )
