from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class Settings(BaseModel):
    omdb_url: str = "http://www.omdbapi.com/"
    omdb_api_key: str = os.getenv("OMDB_API_KEY")

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

def make_request(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

async def get_movies(title: str = Query(...), settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "t": title,
    }
    
    try:
        movies = make_request(settings.omdb_url, params=params)
        
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return JSONResponse(content=response, status_code=404)

        return JSONResponse(content=movies, status_code=200)
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")

async def get_movie_id(id: str = Query(...), settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "i": id,
    }
    
    try:
        movie = make_request(settings.omdb_url, params=params)
        
        if 'Error' in movie:
            response = {
                "status": "fail",
                "message": movie['Error']
            }
            return JSONResponse(content=response, status_code=404)
        
        return JSONResponse(content=movie)
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")

async def health_check():
    response = {
        "status": "success",
        "message": "OMDB API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)