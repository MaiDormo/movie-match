from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests

class Settings(BaseModel):
    stream_avail_url: str = "https://streaming-availability.p.rapidapi.com/shows/search/title"
    stream_avail_api_key: str = os.getenv("stream_avail_API_KEY")
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
    if stream_avail_data and 'streamingOptions' in stream_avail_data[0] and country in stream_avail_data[0]['streamingOptions']:
        streaming_options = stream_avail_data[0]['streamingOptions'][country]
        return [
            {
                "service_name": stream_opts.get("service", {}).get("name", "Unknown"),
                "service_type": stream_opts.get("type", "Unknown"),
                "quality": stream_opts.get("quality", "Unknown")
            }
            for stream_opts in streaming_options
        ]
    return None

def make_stream_request(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

async def get_movie_availability(
    title: str = Query(...),
    country: str = Query(...),
    settings: Settings = Depends(get_settings)
):
    if not title or not country:
        return handle_error(None, 400, "Title and country are required")

    headers = {
        "x-rapidapi-key": settings.stream_avail_api_key,
        "x-rapidapi-host": settings.stream_avail_host
    }
    params = {"country": country, "title": title}

    try:
        stream_avail_data = make_stream_request(settings.stream_avail_url, headers, params)
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

async def health_check():
    response = {
        "status": "success",
        "message": "STREAMING AVAILABILITY API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)