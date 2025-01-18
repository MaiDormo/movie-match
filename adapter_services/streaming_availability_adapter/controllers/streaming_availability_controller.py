from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class Settings(BaseModel):
    stream_avail_url: str = "https://streaming-availability.p.rapidapi.com/shows"
    stream_avail_api_key: str = os.getenv("STREAMING_AVAILABILITY_API_KEY")
    stream_avail_host: str = "streaming-availability.p.rapidapi.com"

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

def filter_data(stream_avail_data, country):
    if stream_avail_data and 'streamingOptions' in stream_avail_data and country in stream_avail_data['streamingOptions']:
        streaming_options = stream_avail_data['streamingOptions'][country]
        
        service_dict = {}  # Dizionario per tenere traccia dei servizi unici
        
        for stream_opts in streaming_options:
            service_name = stream_opts.get("service", {}).get("name", "Unknown")
            service_type = stream_opts.get("type", "Unknown")
            link = stream_opts.get("link", "Unknown")
            logo = stream_opts.get("service", {}).get("imageSet", {}).get("lightThemeImage", None)
            
            # Capitalizzare la prima lettera di service_type
            service_type = service_type.capitalize()
            
            # Se il servizio non è ancora stato aggiunto, lo aggiungiamo
            if service_name not in service_dict:
                service_dict[service_name] = {
                    "service_name": service_name,
                    "links": [link],  # Lista per raccogliere tutti i link
                    "logos": [logo],  # Lista per raccogliere tutti i loghi
                    "service_types": [service_type]  # Lista per raccogliere i tipi di servizio
                }
            else:
                # Aggiungiamo il link, logo e service_type a quelli già esistenti
                existing_service = service_dict[service_name]
                existing_service["links"].append(link)
                existing_service["logos"].append(logo)
                existing_service["service_types"].append(service_type)
        
        # Ora aggiorniamo ogni servizio con il tipo finale (ordinato e concatenato)
        for service_name, service_data in service_dict.items():
            # Ordinare i tipi di servizio in ordine alfabetico e concatenarli con "/"
            sorted_service_types = sorted(set(service_data["service_types"]))
            service_data["service_type"] = "/".join(sorted_service_types)
            
            # Mantenere solo il primo link e logo per ogni servizio
            service_data["link"] = service_data["links"][0]
            service_data["logo"] = service_data["logos"][0]
            
            # Rimuovere le liste di link e loghi poiché non sono più necessarie
            del service_data["links"]
            del service_data["logos"]
        
        # Creare una lista ordinata per service_name
        result = sorted(service_dict.values(), key=lambda x: x['service_name'])
        
        return result
    
    return None



def make_stream_request(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

async def get_movie_availability(
    imdb_id: str = Query(...),
    country: str = Query(...),
    settings: Settings = Depends(get_settings)
):
    if not imdb_id or not country:
        return handle_error(None, 400, "IMDB ID and country are required")

    headers = {
        "x-rapidapi-key": settings.stream_avail_api_key,
        "x-rapidapi-host": settings.stream_avail_host
    }
    url = f"{settings.stream_avail_url}/{imdb_id}"  # Updated endpoint with imdb_id in the path
    params = {"country": country}  # Only country is needed as a query parameter

    try:
        stream_avail_data = make_stream_request(url, headers, params)
        if 'Error' in stream_avail_data:
            return handle_error(None, 404, stream_avail_data['Error'])
        result = filter_data(stream_avail_data, country)
        if result:
            return JSONResponse(content=result, status_code=200)
        return handle_error(None, 404, "No streaming options found for the specified country")
    except requests.exceptions.HTTPError as e:
        return handle_error(e, 404, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the Streaming Availability API")

async def health_check(settings: Settings = Depends(get_settings)):
    response = {
        "status": "success",
        "message": "STREAMING AVAILABILITY API Adapter is up and running! key=" + settings.stream_avail_api_key
    }
    return JSONResponse(content=response, status_code=200)
