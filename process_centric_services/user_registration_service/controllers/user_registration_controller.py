import requests
from fastapi import Body, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from models.user_registration_model import UserRegistration

# Service endpoints
VALID_CHECK_SERVICE_URL = "http://valid-email-service:5000/api/v1/validate-email"
USER_DB_ADAPTER_URL = "http://user-db-adapter:5000/api/v1/user"

def create_response(
    status_code: int, 
    message: str = None, 
    data: Dict[str, Any] = None, 
    status: str = "success"
) -> JSONResponse:
    """Create a standardized JSON response"""
    content = {"status": status}
    if message:
        content["message"] = message
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def handle_service_request(method: str, url: str, **kwargs) -> Dict:
    """Handle external service requests with standardized error handling"""
    try:
        if method.lower() == "get":
            response = requests.get(url, **kwargs)
        elif method.lower() == "post":
            response = requests.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        # Try to get detailed error message from response
        try:
            error_data = response.json()
            error_detail = error_data.get('detail') or error_data.get('message')
            if error_data.get('data'):
                return error_data  # Return the error response directly for validation errors
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail or str(http_err)
            )
        except ValueError:
            raise HTTPException(
                status_code=response.status_code,
                detail=str(http_err)
            )
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is temporarily unavailable. Please try again later."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out. Please try again."
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {req_err}"
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data format: {val_err}"
        )

async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User Registration Service is up and running"
    )

async def registrate_user(user: UserRegistration = Body(...)) -> JSONResponse:
    """Handle user registration process"""
    try:
        # Validate password match
        if user.password != user.password_confirmation:
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                status="fail",
                data={"password": "The password and password confirmation do not match!"}
            )

        # Validate email
        email_validation = handle_service_request(
            "get",
            VALID_CHECK_SERVICE_URL,
            params={"email": user.email}
        )
        
        # Handle email validation errors
        if email_validation.get("status") == "fail" or email_validation.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                status="fail",
                message=email_validation.get("message", "Email validation failed"),
                data=email_validation.get("data") or {"email": email_validation.get("detail", "Invalid email")}
            )

        # Prepare user data for registration
        user_data = {
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "preferences": [28, 14],  # Default preferences
            "password": user.password
        }

        # Register user in database
        try:
            db_response = handle_service_request(
                "post",
                USER_DB_ADAPTER_URL,
                json=user_data
            )
            
            if db_response.get("status") == "fail" or db_response.get("status") == "error":
                return create_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    status="fail",
                    message=db_response.get("message", "User registration failed"),
                    data=db_response.get("data") or {"error": db_response.get("detail", "Registration error")}
                )

        except HTTPException as db_err:
            if db_err.status_code == 400:
                return create_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    status="fail",
                    data={"email": "This email is already registered"}
                )
            raise

        # Return success response
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="User created successfully",
            data={"user": user.model_dump(exclude={"password", "password_confirmation"})}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )