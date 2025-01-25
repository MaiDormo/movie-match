import asyncio
from functools import partial
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx

class Settings(BaseModel):
    """Configuration settings for external service endpoints."""
    omdb_url: str = "http://omdb-adapter:5000/api/v1/search_info"
    genres_url: str = "http://genres-db-adapter:5000/api/v1/genres"
    preferences_url: str = "http://user-db-adapter:5000/api/v1/user"
    tmdb_url: str = "http://tmdb-adapter:5000/api/v1/discover-movies"
    tmdb_movie_url: str = "http://tmdb-adapter:5000/api/v1/movie"
    
    timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0

def get_settings() -> Settings:
    """
    Factory function for Settings dependency injection.
    
    Returns:
        Settings: Configuration object with service URLs
    """
    return Settings()

async def fetch_data(url: str, method: str = "GET", params: dict = None, settings: Settings = None) -> Dict[str, Any] | None:
    """Generic function to fetch data from external services with retry logic."""
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
    
def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """
    Create a standardized API response.
    
    Args:
        status_code (int): HTTP status code
        message (str): Response message
        data (Dict[str, Any], optional): Response payload. Defaults to None.
    
    Returns:
        JSONResponse: Formatted API response
    """
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def get_text_movie_search(query: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    try:
        # Ottieni generi e preferenze in parallelo
        movie_list_data = await fetch_data(url=settings.omdb_url, params={"title": query}, settings=settings)

        if isinstance(movie_list_data, JSONResponse):
            return movie_list_data

        # Ordina i film per valutazione
        movie_list_data.get("data").sort(key=lambda x: x["imdbRating"], reverse=True)

        # Risposta di successo
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies retrieved successfully",
            data={"movie_list": movie_list_data.get("data", {})}
        )

    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data={"error": str(e)}
        )

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

        if not movie_list_data or movie_list_data.get("status") != "success":
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="TMDB service unavailable"
            )

        movies = movie_list_data["data"]["movie_list"]
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

                if details_response.get("status") == "success":
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

    
    

async def get_user_genres(user_id: str, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """
    Combina generi e preferenze utente in un'unica risposta JSON.
    Utilizza la funzione fetch_data per ottenere i dati con logica di retry.
    """
    try:
        # Ottieni generi e preferenze in parallelo
        genres_data, preferences_data = await asyncio.gather(
            fetch_data(url=settings.genres_url, settings=settings),
            fetch_data(url=settings.preferences_url, params={"id": user_id}, settings=settings),
            return_exceptions=True
        )
        if not genres_data:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="GENRE DATABASE service unavailable"
            )
        if not preferences_data:
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="USER DATABASE service unavailable"
            )
        
        if isinstance(genres_data, JSONResponse):
            return genres_data
        
        if isinstance(preferences_data, JSONResponse):
            return preferences_data

        # Validazione e mapping dei dati
        if "genres" not in genres_data.get("data", {}):
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="Invalid or missing genres data"
            )

        if not preferences_data or "preferences" not in preferences_data.get("data", {}):
            return create_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="Invalid or missing user preferences data"
            )

        genres = [
            {"genreId": genre["genreId"], "name": genre["name"]}
            for genre in genres_data["data"]["genres"]
        ]
        preferences = preferences_data["data"]["preferences"]

        # Combina i generi con le preferenze
        result = [
            {**genre, "isPreferred": genre["genreId"] in preferences}
            for genre in genres
        ]

        # Risposta di successo
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Genres and user preferences retrieved successfully",
            data={"user_genres": result}
        )

    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            data={"error": str(e)}
        )
    
async def update_user_preferences(
    id: str = Query(
        ...,
        description="Unique identifier of the user whose preferences are to be updated",
        example="0b8ac00c-a52b-4649-bd75-699b49c00ce3"
    ),
    preferences: list[int] = Body(
        ...,
        description="List of updated preference IDs",
        example=[28, 35, 12]
    ),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """
    Update user preferences by making a PUT request to the user service.

    Args:
        user_id (str): Unique identifier of the user.
        preferences (list[int]): List of updated preference IDs.
        settings (Settings): Dependency injection for service URLs.

    Returns:
        JSONResponse: A standardized API response indicating success or failure.
    """
    url = f"{settings.preferences_url}?id={id}"
    payload = {"preferences": preferences}

    try:
        response = await fetch_data(url=url, method="PUT", params=payload, settings=settings)
        return response
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while updating preferences.",
            data={"error:": str(e)+url}
        )



async def health_check():
    return create_response(
        status_code=200,
        message="Movie Details Service is up and running!"
    )