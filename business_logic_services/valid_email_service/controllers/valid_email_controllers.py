from typing import Dict, Any, Tuple
import requests
from fastapi import Query, status
from fastapi.responses import JSONResponse

# Constants
EMAIL_CHECK_ADAPTER_URL = "http://email-check-adapter:5000/api/v1/email"
REQUEST_TIMEOUT = 10  # seconds

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content.update(data)
    return JSONResponse(content=content, status_code=status_code)

def parse_email_check_response(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Parse and validate email check response.
    
    Returns:
        Tuple[bool, Dict]: (is_valid, response_data)
    """
    email_check = data.get('data', {}).get('email_check', {})
    email = email_check.get('email', '')
    
    # Check format validity
    if email_check.get('is_valid_format') == "FALSE":
        return False, {
            "email": f"Invalid email format. Please provide a valid email address."
        }
    
    # Check deliverability
    if email_check.get('deliverability') == "UNDELIVERABLE":
        return False, {
            "email": f"The email address '{email}' appears to be unreachable."
        }
        
    # Email is valid
    return True, {
        "email": email,
        "valid": "true",
        "message": "Email validation successful"
    }

async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Valid Email Business Logic Service is up and running"
    )

async def validate_email(
    email: str = Query(..., description="Email address to validate")
) -> JSONResponse:
    """
    Validate an email address using the email check adapter service.
    
    Args:
        email: The email address to validate
        
    Returns:
        JSONResponse with validation results
        
    Raises:
        create_response: For various error conditions
    """
    params = {"email": email}
    
    try:
        # Make request to email check adapter
        response = requests.get(
            EMAIL_CHECK_ADAPTER_URL, 
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        adapter_response = response.json()

        # Handle adapter error responses
        if adapter_response.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                status="fail",
                message=adapter_response.get("message", "Email validation failed"),
                data={"email": adapter_response.get("message", "Unknown error occurred")}
            )

        # Parse and validate the response
        is_valid, validation_data = parse_email_check_response(adapter_response)
        
        if not is_valid:
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                status="fail",
                message="Email validation failed",
                data=validation_data
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Email validation successful",
            data={"email_check": validation_data}
        )

    except requests.exceptions.HTTPError as http_err:
        raise create_response(
            status_code=response.status_code,
            message=f"Email validation service error: {http_err}"
        )
    except requests.exceptions.ConnectionError:
        raise create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Email validation service is temporarily unavailable"
        )
    except requests.exceptions.Timeout:
        raise create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Email validation request timed out"
        )
    except requests.exceptions.RequestException as req_err:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error occurred during email validation: {req_err}"
        )
    except ValueError as json_err:
        raise create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Invalid response format from email validation service: {json_err}"
        )