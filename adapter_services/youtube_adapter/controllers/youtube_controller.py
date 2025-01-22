from typing import Any, Dict
from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class Settings(BaseModel):
    youtube_search_url: str = "https://www.googleapis.com/youtube/v3/search"
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY")

def get_settings():
    """Dependency injection for YouTube configuration"""
    return Settings()


def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def make_request(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def health_check(settings: Settings = Depends(get_settings)) -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=200,
        message="YOUTUBE API Adapter is up and running!"
    )

async def search_youtube(query: str = Query(...), settings: Settings = Depends(get_settings)) -> JSONResponse:
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
            return create_response(
                status_code=404,
                message="Nessun video trovato per la query fornita"
            )

        # Estrai l'ID video e costruisci l'URL embed
        video_id = result["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/embed/{video_id}"
        return create_response(
            status_code=200,
            message="Youtube video successfully retrived!",
            data={
                "video_id": video_id,
                "embed_url": video_url
            }
        )

    except requests.exceptions.HTTPError as e:
        return create_response(
            status_code=404,
            message="Errore HTTP durante la chiamata all'API di YouTube",
            data = str(e))
    except requests.exceptions.ConnectionError as e:
        return create_response(
                status_code=503,
                message="Errore di connessione durante la chiamata all'API di YouTube",
                data = str(e))
    except requests.exceptions.Timeout as e:
        return create_response(
            status_code=504,
            message="Timeout durante la chiamata all'API di YouTube",
            data = str(e))
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=500,
            message="Errore generico durante la chiamata all'API di YouTube",
            data = str(e))

