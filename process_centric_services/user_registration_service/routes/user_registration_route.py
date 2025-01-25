from fastapi import APIRouter
from controllers.user_registration_controller import health_check, registrate_user
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

router = APIRouter()

# Response Models
class ValidationError(BaseModel):
    field: str = Field(..., description="Path to the field that failed validation")
    message: str = Field(..., description="Description of the validation error")
    type: str = Field(..., description="Type of validation error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "body -> password",
                "message": "field required",
                "type": "missing"
            }
        }

class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class BaseResponseWithData(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "User created successfully",
                "data": {
                    "user": {
                        "name": "John",
                        "surname": "Doe",
                        "email": "john.doe@example.com"
                    }
                }
            }
        }

class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any] | List[ValidationError]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "body -> password",
                        "message": "field required",
                        "type": "missing"
                    }
                ]
            }
        }

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the User Registration Service is running",
    responses={
        200: {
            "description": "Service is running",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User Registration Service is up and running"
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The HTTP method is not allowed for this endpoint"
                    }
                }
            }
        },
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)(health_check)

router.post(
    "/api/v1/registrate-user",
    status_code=201,
    response_model=BaseResponseWithData,
    summary="Register New User",
    description="Register a new user with email validation and creation in database",
    responses={
        201: {
            "description": "User registered successfully",
            "model": BaseResponseWithData
        },
        400: {
            "description": "Bad request",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "password_mismatch": {
                            "value": {
                                "status": "error",
                                "message": "Validation failed",
                                "data": {"password": "The password and password confirmation do not match!"}
                            }
                        },
                        "email_exists": {
                            "value": {
                                "status": "error",
                                "message": "Registration failed",
                                "data": {"email": "This email is already registered"}
                            }
                        }
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The HTTP method is not allowed for this endpoint"
                    }
                }
            }
        },
        422: {
            "description": "Validation error", 
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "body -> password",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Internal server error", "model": ErrorResponse},
        503: {
            "description": "Service unavailable",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Service is temporarily unavailable. Please try again later."
                    }
                }
            }
        },
        504: {
            "description": "Gateway timeout",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request timed out. Please try again."
                    }
                }
            }
        }
    }
)(registrate_user)