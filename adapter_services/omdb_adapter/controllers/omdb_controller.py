from fastapi import Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class MovieQuery(BaseModel):
    t: str

class MovieIDQuery(BaseModel):
    i: str

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
        "error": str(e)
    }
    return JSONResponse(content=response, status_code=status_code)

async def get_movies(query: MovieQuery, settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "t": query.t,
    }
    
    try:
        response = requests.get(settings.omdb_url, params=params)
        response.raise_for_status()
        movies = response.json()
        
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return JSONResponse(content=response, status_code=404)
        
        return JSONResponse(content=movies)
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")

async def get_movie_id(query: MovieIDQuery, settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "i": query.i,
    }
    
    try:
        response = requests.get(settings.omdb_url, params=params)
        response.raise_for_status()
        movie = response.json()
        
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