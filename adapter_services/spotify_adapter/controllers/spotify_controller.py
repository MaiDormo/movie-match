import requests
from bs4 import BeautifulSoup
from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

class Settings(BaseModel):
    spotify_url: str = "https://api.spotify.com/v1/search"
    spotify_track_url: str = "https://api.spotify.com/v1/tracks"
    spotify_auth_url: str = "https://accounts.spotify.com/api/token"
    spotify_client_id: str = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET")
    

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

def make_request(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_spotify_access_token(settings: Settings) -> str:
    response = requests.post(
        settings.spotify_auth_url,
        data={"grant_type": "client_credentials"},
        auth=(settings.spotify_client_id, settings.spotify_client_secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]

def search_song_on_spotify(song_name: str, access_token: str, settings: Settings) -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": song_name,
        "type": "track",
        "limit": 1,
        "market": "US"
    }
    data = make_request(settings.spotify_url, headers, params)  

    if data["tracks"]["items"]:
        track = data["tracks"]["items"][0]
        return track["id"]
    return None

def get_track_preview_url(track_id: str, access_token: str, settings: Settings) -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{settings.spotify_track_url}/{track_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    track_data = response.json()

    preview_url = track_data.get("preview_url")
    if not preview_url:
        raise ValueError(f"Anteprima per il brano con ID {track_id} non disponibile.")
    return preview_url

def get_track_details(track_id: str, access_token: str, settings: Settings) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{settings.spotify_track_url}/{track_id}"
    params = {
        "market": "US"  # Aggiungi il parametro 'market' alla richiesta dei dettagli
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    track_data = response.json()

    # Restituire tutti i dettagli della canzone
    track_details = {
        "song_name": track_data.get("name"),
        "artist": track_data["artists"][0]["name"],
        "album": track_data["album"]["name"],
        "preview_url": track_data.get("preview_url"),
        "spotify_url": track_data["external_urls"]["spotify"],
        "track_id": track_data["id"],
        "popularity": track_data.get("popularity"),
        "duration_ms": track_data.get("duration_ms"),
        "explicit": track_data.get("explicit"),
        "release_date": track_data.get("album", {}).get("release_date")
    }
    return track_details

def get_preview_from_embed(track_id: str) -> str:
    # Creiamo il link dell'embed per ottenere il preview_url
    embed_url = f"https://open.spotify.com/embed/track/{track_id}"
    response = requests.get(embed_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Cerca l'elemento #resource che contiene i dettagli della traccia
    resource_element = soup.find(id="resource")
    if resource_element:
        track_details = resource_element.get('data-resource')
        return track_details.get("preview_url", None)
    return None


async def get_song(
    song_name: str = Query(..., description="Nome della canzone da cercare"),
    settings: Settings = Depends(get_settings)
):
    try:
        # Ottieni il token di accesso
        access_token = get_spotify_access_token(settings)

        # Cerca la canzone su Spotify e ottieni l'ID
        track_id = search_song_on_spotify(song_name, access_token, settings)
        if not track_id:
            return JSONResponse(content={"message": "No track found"}, status_code=404)

        # Ottieni tutti i dettagli della canzone utilizzando l'ID
        track_details = get_track_details(track_id, access_token, settings)

        return track_details

    except requests.RequestException as e:
        return handle_error(e, 500, "Errore durante la ricerca della canzone")
    except ValueError as e:
        return handle_error(e, 500, str(e))
    except Exception as e:
        return handle_error(e, 500, "Errore interno del server")




def search_playlist_on_spotify(playlist_name: str, access_token: str, settings: Settings):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": playlist_name,   # Nome della playlist
        "type": "playlist",    # Tipo di ricerca (playlist)
        "limit": 1,            # Limita a 1 risultato
        "market": "US"         # Parametro 'market' per la ricerca geografica
    }
    response = requests.get(settings.spotify_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("playlists") and data["playlists"].get("items"):
        # Se la risposta contiene delle playlist, ritorna l'ID della prima playlist
        playlist = data["playlists"]["items"][0]
        return playlist["id"]
    return None

def get_playlist_url(playlist_id: str, access_token: str, settings: Settings) -> str:
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    playlist_data = response.json()

    return playlist_data["external_urls"]["spotify"]

def get_playlist_info(
    playlist_name: str = Query(..., description="Nome della playlist da cercare"),
    settings: Settings = Depends(get_settings)
):
    try:
        # Ottieni il token di accesso
        access_token = get_spotify_access_token(settings)

        # Cerca la playlist su Spotify e ottieni l'ID
        playlist_id = search_playlist_on_spotify(playlist_name, access_token, settings)
        if not playlist_id:
            return JSONResponse(content={"message": "No playlist found"}, status_code=404)

        # Ottieni i dettagli della playlist
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        playlist_data = response.json()

        # Estrai i dati richiesti
        spotify_url = playlist_data.get("external_urls", {}).get("spotify")
        cover_url = playlist_data.get("images", [{}])[0].get("url")  # Usa il primo elemento di "images"
        name = playlist_data.get("name")

        # Verifica che i dati siano validi
        if not spotify_url or not cover_url or not name:
            return JSONResponse(content={"message": "Incomplete playlist data"}, status_code=500)

        # Restituisci i dati formattati
        return {
            "spotify_url": spotify_url,
            "cover_url": cover_url,
            "name": name
        }

    except requests.RequestException as e:
        return handle_error(e, 500, "Errore durante la ricerca della playlist")
    except Exception as e:
        return handle_error(e, 500, "Errore interno del server")


def get_playlist_tracks(playlist_id: str, access_token: str, settings: Settings):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {
        "market": "US"  # Aggiungi il parametro 'market' alla richiesta dei dettagli
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    track_data = response.json()

    if track_data.get("items"):
        tracks = []
        for track_item in track_data["items"][:10]:  # Limitati alle prime 10 tracce
            track = track_item["track"]
            tracks.append({
                "song_name": track["name"],
                "track_id": track["id"],
                "preview_url": track.get("preview_url"),
            })
        return tracks
    return []


async def get_playlist(
    playlist_name: str = Query(..., description="Nome della playlist da cercare"),
    settings: Settings = Depends(get_settings)
):
    try:
        # Ottieni il token di accesso
        access_token = get_spotify_access_token(settings)

        # Cerca la playlist su Spotify e ottieni l'ID
        playlist_id = search_playlist_on_spotify(playlist_name, access_token, settings)
        if not playlist_id:
            return JSONResponse(content={"message": "No playlist found"}, status_code=404)

        # Ottieni l'URL della playlist
        playlist_url = get_playlist_url(playlist_id, access_token, settings)

        return {"playlist_url": playlist_url}

    except requests.RequestException as e:
        return handle_error(e, 500, "Errore durante la ricerca della playlist")
    except Exception as e:
        return handle_error(e, 500, "Errore interno del server")


async def health_check():
    response = {
        "status": "success",
        "message": "SPOTIFY API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)