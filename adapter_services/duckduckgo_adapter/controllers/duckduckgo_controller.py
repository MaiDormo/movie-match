from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from duckduckgo_search import DDGS

import os
import requests

class Settings(BaseModel):
    groq_url: str = ""
    duckduckgo_api_key: str = os.getenv("DUCKDUCKGO_API_KEY")

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


async def health_check():
    response = {
        "status": "success",
        "message": "DUCKDUCKGO API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)

def perform_image_search(movie_title: str = Query(...)):
    results = None
    query = movie_title + " movie poster"
    
    try:
        # Perform an image search using DuckDuckGo with the specified query
        ddgs = DDGS()
        results = ddgs.images(
            keywords=query,  # Search keywords
            max_results=1,   # Limit the results to 1 image
        )
        
        if not results:
            return JSONResponse(
                content={"status": "error", "message": "No image found for the specified movie title"},
                status_code=404
            )
        
        # Return the URL of the first image result
        print(f"[IMAGE SEARCH RESULT]: {results}")
        return {"image_url": results[0]["image"]}

    # Gestione degli errori HTTP
    except requests.exceptions.HTTPError as e:
        return JSONResponse(
            content={"status": "error", "message": f"HTTP error occurred: {str(e)}"},
            status_code=404
        )
    except requests.exceptions.ConnectionError as e:
        return JSONResponse(
            content={"status": "error", "message": "Connection error occurred"},
            status_code=503
        )
    except requests.exceptions.Timeout as e:
        return JSONResponse(
            content={"status": "error", "message": "Request timed out"},
            status_code=504
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"status": "error", "message": f"An error occurred while calling the image search: {str(e)}"},
            status_code=500
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": f"An unexpected error occurred: {str(e)}"},
            status_code=500
        )

