from fastapi import APIRouter
from controllers.user_login_controller import health_check, login, refresh_token
from fastapi.security import OAuth2PasswordRequestForm
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

class TokenResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="Token data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
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
    description="Check if the User Login Service is running",
    responses={
        200: {
            "description": "Service is running",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "User Login Service is up and running!"
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
                        "code": 405,
                        "message": "The HTTP method is not allowed for this endpoint"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)(health_check)

router.post(
    "/api/v1/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user and return access token",
    responses={
        200: {
            "description": "Successfully authenticated",
            "model": TokenResponse
        },
        400: {
            "description": "Bad request",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "missing_credentials": {
                            "value": {
                                "status": "error",
                                "code": 400,
                                "message": "Email and password are required"
                            }
                        },
                        "invalid_password": {
                            "value": {
                                "status": "error",
                                "code": 400,
                                "message": "Invalid password"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 404,
                        "message": "Email not found. Please check your email and try again."
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
                        "code": 405,
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
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 500,
                        "message": "An internal server error occurred"
                    }
                }
            }
        },
        504: {
            "description": "Gateway timeout",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 504,
                        "message": "Database service timeout"
                    }
                }
            }
        }
    }
)(login)

router.post(
    "/api/v1/refresh-token",
    response_model=TokenResponse,
    summary="Refresh Token",
    description="Refresh an existing access token",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "model": TokenResponse
        },
        401: {
            "description": "Invalid or expired token",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "value": {
                                "status": "error",
                                "code": 401,
                                "message": "Invalid token format"
                            }
                        },
                        "expired_token": {
                            "value": {
                                "status": "error",
                                "code": 401,
                                "message": "Token has expired"
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
                        "code": 405,
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
                                "field": "header -> authorization",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)(refresh_token)