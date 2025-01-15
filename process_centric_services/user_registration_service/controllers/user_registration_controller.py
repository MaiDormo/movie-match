import requests
from fastapi import Body, HTTPException
from fastapi.responses import JSONResponse
from models.user_registration_model import UserRegistration

VALID_CHECK_SERVICE_URL = "http://valid-email-service:5000/api/v1/validate-email"
USER_DB_ADAPTER_URL = "http://user-db-adapter:5000/api/v1/user"

async def health_check():
    response = {
        "status": "success",
        "message": "User Registration Service is up and running"
    }
    return JSONResponse(content=response, status_code=200)

async def registrate_user(user: UserRegistration = Body(...)):
    
    if user.password != user.password_confirmation:
        response = {
            "status": "fail",
            "data": {
                "password": "The password and password confirmation do not match!"
            }
        }
        return JSONResponse(content=response, status_code=400)
    
    params = {"email": user.email}
    
    try:
        response = requests.get(VALID_CHECK_SERVICE_URL, params=params)
        response.raise_for_status()
        external_response = response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        raise HTTPException(status_code=503, detail=f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        raise HTTPException(status_code=504, detail=f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {req_err}")
    except ValueError as json_err:
        raise HTTPException(status_code=500, detail=f"JSON decoding error: {json_err}")
    
    if external_response["status"] == "fail":
        reponse = {
            "status": "fail",
            "data": external_response.get("data")
        }
        return JSONResponse(content=response, status_code=400)
    
    user_registered = {
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "preferences": ["action", "comedy"],
        "password": user.password
    }

    try: 
        response = requests.post(USER_DB_ADAPTER_URL, json=user_registered)
        response.raise_for_status()
        external_response = response.json()
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        raise HTTPException(status_code=503, detail=f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        raise HTTPException(status_code=504, detail=f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {req_err}")
    except ValueError as json_err:
        raise HTTPException(status_code=500, detail=f"JSON decoding error: {json_err}")
    
    response = {
        "status": "success",
        "message": "User created successfully",
        "data": {
            "user": user.model_dump
        }
    }
    
    return JSONResponse(content=response, status_code=200)
    
    
        