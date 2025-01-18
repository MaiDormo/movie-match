from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class Settings(BaseModel):
    youtube_search_url: str = "https://www.googleapis.com/youtube/v3/search"
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY")

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


async def health_check(settings: Settings = Depends(get_settings)):
    response = {
        "status": "success",
        "message": "YOUTUBE API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)

async def search_youtube(query: str = Query(...), settings: Settings = Depends(get_settings)):
    """
    Cerca un video su YouTube utilizzando una stringa di query e restituisce l'ID del video o l'URL embed.
    """
    
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",  # Cerca solo video
        "maxResults": 1,  # Ritorna il primo risultato
        "key": settings.youtube_api_key,
    }

    try:
        # Esegui la richiesta
        result = make_request(settings.youtube_search_url, params)

        # Controlla se ci sono risultati
        if "items" not in result or len(result["items"]) == 0:
            response = {
                "status": "fail",
                "message": "Nessun video trovato per la query fornita."
            }
            return JSONResponse(content=response, status_code=404)

        # Estrai l'ID video e costruisci l'URL embed
        video_id = result["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/embed/{video_id}"
        return JSONResponse(content={"video_id": video_id, "embed_url": video_url}, status_code=200)

    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "Errore HTTP durante la chiamata all'API di YouTube")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Errore di connessione durante la chiamata all'API di YouTube")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Timeout durante la chiamata all'API di YouTube")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "Errore generico durante la chiamata all'API di YouTube")

