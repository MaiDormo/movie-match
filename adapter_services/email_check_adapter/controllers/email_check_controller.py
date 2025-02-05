import os
from typing import Dict, Any
from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from pydantic import BaseModel, Field, HttpUrl
import requests

class Settings(BaseModel):
    """Configuration settings for the email validation service"""
    url: HttpUrl = Field(
        default="https://emailvalidation.abstractapi.com/v1/",
        description="Base URL for the Abstract Email Validation API"
    )
    api_key: str = Field(
        default=os.getenv("ABSTRACT_API_KEY"),
        description="API key for authenticating with Abstract Email Validation API"
    )
    timeout: int = Field(
        default=10,
        description="Request timeout in seconds",
        ge=1,
        le=30
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://emailvalidation.abstractapi.com/v1/",
                "api_key": "your_api_key_here",
                "timeout": 10
            }
        }

def get_settings() -> Settings:
    """Get application settings with validation"""
    settings = Settings()
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured"
        )
    return settings

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
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
    email: str = Query(
        ..., 
        description="Email address to validate",
        example="user@example.com",
    ),
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
            data= filter_response(data)
        )

    except HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err}"
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_msg = "API rate limit exceeded"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_msg = "Invalid API key"
            
        raise create_response(
            status_code=response.status_code,
            message=error_msg
        )
        
    except ConnectionError:
        raise create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Email validation service is temporarily unavailable"
        )
        
    except Timeout:
        raise create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Email validation service request timed out"
        )
        
    except ValueError as json_err:
        raise create_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message=f"Invalid JSON response from email validation service: {json_err}"
        )
        
    except RequestException as req_err:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to validate email: {req_err}"
        )