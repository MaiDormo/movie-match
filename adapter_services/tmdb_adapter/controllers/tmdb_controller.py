from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests
import re

class Settings(BaseModel):
    tmdb_url: str = "https://api.themoviedb.org/3/search/multi"
    tmdb_url_id: str = "https://api.themoviedb.org/3/find"
    tmdb_api_key: str = os.getenv("TMDB_API_KEY")

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
        "language": language,
        "external_source": "imdb_id",
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


async def health_check():
    response = {
        "status": "success",
        "message": "TMDB API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)