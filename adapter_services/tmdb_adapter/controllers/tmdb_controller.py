from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests
import re

class Settings(BaseModel):
    tmdb_url: str = "https://api.themoviedb.org/3/search/multi"
    tmdb_url_id: str = "https://api.themoviedb.org/3/find/external_id"
    tmdb_discover_movie: str = "https://api.themoviedb.org/3/discover/movie"
    tmdb_api_key: str = os.getenv("TMDB_API_KEY")
    external_source: str = "imdb_id"

def get_settings():
    return Settings()

def handle_error(e, status_code, message):
    response = {
        "status": "error",
        "code": status_code,
        "message": message,
        "error": str(e) if e else None
    }
    return JSONResponse(content=response, status_code=status_code)

def make_request(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def is_valid_language(language: str) -> bool:
    pattern = re.compile(r'^[a-z]{2}-[A-Z]{2}$')
    return bool(pattern.match(language))


def filter_data(tmdb_data):
    return tmdb_data["results"][0]

async def get_movie_popularity(
        title: str = Query(...), 
        language: str = Query(...), 
        settings: Settings = Depends(get_settings)):
    
    # Check if id and language are present and validate language format
    if not title or not language:
        return handle_error(None, 400, "ID and language are required")
    
    if not is_valid_language(language):
        return handle_error(None, 400, "Invalid language format. Expected format: en-US, de-DE, it-IT, etc.")
    
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + settings.tmdb_api_key
    }

    params = {
        "query": title,
        "language": language,
    }

    try:
        movies = make_request(settings.tmdb_url, headers, params)
        
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return JSONResponse(content=response, status_code=404)
        
        movie = filter_data(movies)
        return JSONResponse(content=movie, status_code=200)
    
    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the TMDB API")


async def get_movie_popularity_id(
        id: str = Query(...), 
        language: str = Query(...), 
        settings: Settings = Depends(get_settings)):
    
    # Check if id and language are present and validate language format
    if not id or not language:
        return handle_error(None, 400, "ID and language are required")
    
    if not is_valid_language(language):
        return handle_error(None, 400, "Invalid language format. Expected format: en-US, de-DE, it-IT, etc.")
    
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + settings.tmdb_api_key
    }

    params = {
        "external_id": id,
        "language": language,
        "external_source": settings.external_source,
    }

    try:    
        movies = make_request(settings.tmdb_url_id + "/{id}", headers, params)
        
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return JSONResponse(content=response, status_code=404)
        return JSONResponse(content=movies, status_code=200)
    
    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the TMDB API")
    

async def discover_movies(
        language: str = Query(...), 
        with_genres: str = Query(...), 
        vote_avg_gt: float = Query(...), 
        sort_by: str = Query(default="popularity.desc", description="Sort results by this value"),
        settings: Settings = Depends(get_settings)
    ):
    # Validate language format
    if not is_valid_language(language):
        return handle_error(None, 400, "Invalid language format. Expected format: en-US, de-DE, it-IT, etc.")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.tmdb_api_key}"
    }

    params = {
        "language": language,
        "with_genres": with_genres,
        "vote_average.gte": vote_avg_gt,
        "sort_by": sort_by,
        "include_adult": False,
        "include_video": False,
        "page": 1
    }

    try:
        movies = make_request(settings.tmdb_discover_movie, headers, params)
        
        if not movies.get("results"):
            response = {
                "status": "fail",
                "message": "No movies found matching the criteria"
            }
            return JSONResponse(content=response, status_code=404)

        return JSONResponse(content={
            "status": "success",
            "total_results": movies["total_results"],
            "total_pages": movies["total_pages"],
            "results": movies["results"]
        }, status_code=200)
    
    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the TMDB API")



async def health_check():
    response = {
        "status": "success",
        "message": "TMDB API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)