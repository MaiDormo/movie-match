import os
from fastapi import Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from pydantic import BaseModel
import requests


class Settings(BaseModel):
    url: str = "https://emailvalidation.abstractapi.com/v1/"
    api_key: str = os.getenv("ABSTRACT_API_KEY")

def get_settings():
    return Settings()

async def health_check():
    response = {
        "status": "success",
        "message": "Email Checker API Adapter is up and running"
    }
    return JSONResponse(content=response, status_code=200)

async def check_email(email: str = Query(...), settings: Settings = Depends(get_settings)):
    
    params = {
        "api_key": settings.api_key,
        "email": email
    }
    
    try:
        response = requests.get(settings.url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except ConnectionError as conn_err:
        raise HTTPException(status_code=503, detail=f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        raise HTTPException(status_code=504, detail=f"Timeout error occurred: {timeout_err}")
    except RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {req_err}")
    
    try:
        data = response.json()
    except ValueError as json_err:
        raise HTTPException(status_code=500, detail=f"JSON decoding error: {json_err}")

    response = {
        "status": "success",
        "message": "Email check retrieved successfully",
        "data": {
            "email_check": filter_response(data)
        }
    }
    return JSONResponse(content=response, status_code=200)


def filter_response(data):
    filtered_response = {
        "email": data["email"],
        "deliverability": data["deliverability"],
        "is_valid_format": data["is_valid_format"]["text"]
    }
    return filtered_response