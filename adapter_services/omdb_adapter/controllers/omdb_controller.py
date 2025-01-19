from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests
from typing import List
import json

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

def make_request(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

async def get_movies(title: str = Query(...), settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "s": title,  # changed to be the search parameter
        "type": "movie"
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
        return handle_error(e, 404, "HTTP error occurred")
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
        
        return movie
    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")


# Nuova funzione get_movies_with_info
async def get_movies_with_info(title: str = Query(...), settings: Settings = Depends(get_settings)):
    params = {
        "apikey": settings.omdb_api_key,
        "s": title,  # Cambiato per essere il parametro di ricerca
        "type": "movie"
    }
    
    try:
        # Effettua la richiesta al servizio OMDB
        movies = make_request(settings.omdb_url, params=params)
        
        # Controlla se c'è un errore nella risposta
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return JSONResponse(content=response, status_code=404)
        
        # Estrai solo la lista dei film dalla chiave "Search"
        films_list = movies.get("Search", [])

        # Lista per salvare i film con dettagli aggiuntivi
        detailed_movies = []

        for movie in films_list:
            # Ottieni i dettagli del film usando l'ID
            movie_details = await get_movie_id(id=movie["imdbID"], settings=settings)
            
            # Aggiungi i campi "Genre" e "imdbRating" al film originale
            movie_with_details = {
                **movie,
                "Genre": movie_details.get("Genre", "N/A"),
                "imdbRating": movie_details.get("imdbRating", "N/A")
            }
            detailed_movies.append(movie_with_details)

        # Restituisci la lista dei film con i dettagli aggiuntivi
        return JSONResponse(content=detailed_movies, status_code=200)

    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
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