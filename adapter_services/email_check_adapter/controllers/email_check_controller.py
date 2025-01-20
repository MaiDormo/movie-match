import os
from typing import Dict, Any
from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from pydantic import BaseModel, HttpUrl
import requests

class Settings(BaseModel):
    """Configuration settings for the email validation service"""
    url: HttpUrl = "https://emailvalidation.abstractapi.com/v1/"
    api_key: str = os.getenv("ABSTRACT_API_KEY")
    timeout: int = 10  # seconds

def get_settings() -> Settings:
    """Get application settings with validation"""
    settings = Settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured"
        )
    return settings

def create_response(
    status_code: int,
    message: str,
    data: Dict[str, Any] = None,
    status_str: str = "success"
) -> JSONResponse:
    """Create a standardized JSON response"""
    content = {
        "status": status_str,
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def filter_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and format relevant email validation data"""
    try:
        return {
            "email": data["email"],
            "deliverability": data["deliverability"],
            "is_valid_format": data["is_valid_format"]["text"]
        }
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid response format from email validation service: missing {str(e)}"
        )

async def health_check() -> JSONResponse:
    """Service health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Email Checker API Adapter is up and running"
    )

async def check_email(
    email: str = Query(..., description="Email address to validate"),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """
    Validate an email address using the Abstract API service
    
    Args:
        email: Email address to validate
        settings: Application settings
        
    Returns:
        JSONResponse containing validation results
        
    Raises:
        HTTPException: For various error conditions
    """
    params = {
        "api_key": settings.api_key,
        "email": email
    }
    
    try:
        # Make request with timeout
        response = requests.get(
            str(settings.url), 
            params=params,
            timeout=settings.timeout
        )
        response.raise_for_status()
        
        # Parse response data
        data = response.json()
        
        # Filter and return response
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Email check retrieved successfully",
            data={"email_check": filter_response(data)}
        )

    except HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err}"
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_msg = "API rate limit exceeded"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_msg = "Invalid API key"
            
        raise HTTPException(
            status_code=response.status_code,
            detail=error_msg
        )
        
    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email validation service is temporarily unavailable"
        )
        
    except Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Email validation service request timed out"
        )
        
    except ValueError as json_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid JSON response from email validation service: {json_err}"
        )
        
    except RequestException as req_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate email: {req_err}"
        )