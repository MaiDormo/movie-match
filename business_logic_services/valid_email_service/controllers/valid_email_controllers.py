import requests
from fastapi import Query, HTTPException
from fastapi.responses import JSONResponse

EMAIL_CHECK_ADAPTER_URL = "http://email-check-adapter:5000/api/v1/email"

async def health_check():
    response = {
        "status": "success",
        "message": "Valid Email Business Logic Service is up and running",
    }
    return JSONResponse(content=response, status_code=200)

def filter_response(data):
    return {
        "email": data['data']['email_check']['email'],
        "valid": "true"
    }


async def validate_email(email: str = Query(...)):
    params = {"email": email}
    
    try:
        response = requests.get(EMAIL_CHECK_ADAPTER_URL, params=params) 
        response.raise_for_status()
        data = response.json()
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

    if data.get('data').get('email_check').get('deliverability') == "UNDELIVERABLE":
        cause = {
            "email": f"The email provided '{data.get('data').get('email_check').get('email')}' is not in the correct format"
        } if data.get('data').get('email_check').get('is_valid_format') == "FALSE" else {
            "email": f"The email provided '{data.get('data').get('email_check').get('email')}' cannot be found"
        }
        
        response = {
            "status": "fail",
            "data": cause
        }
        return JSONResponse(content=response, status_code=400)

    response = {
        "status": "success",
        "message": "Email check retrieved successfully",
        "data": {
            "email_check": filter_response(data)
        }
    }
    return JSONResponse(content=response, status_code=200)