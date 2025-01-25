from fastapi import APIRouter
from controllers.email_check_controller import health_check, check_email
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Email Check Service is up and running"
            }
        }

class EmailValidationResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Email validation details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Email validation successful",
                "data": {
                    "email": "user@example.com",
                    "deliverability": "DELIVERABLE",
                    "is_valid_format": "TRUE"
                }
            }
        }

class ValidationError(BaseModel):
    field: str = Field(..., description="Path to the field that failed validation")
    message: str = Field(..., description="Description of the validation error")
    type: str = Field(..., description="Type of validation error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> email",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 422,
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "query -> email",
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
    description="Check if the Email Checker API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Email Check Service is up and running"
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
        }
    }
)(health_check)

router.get(
    "/api/v1/email",
    response_model=EmailValidationResponse,
    summary="Validate Email",
    description="Validate an email address using the Abstract Email Validation API",
    responses={
        200: {
            "description": "Email validation completed successfully",
            "model": EmailValidationResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "valid_email": {
                            "value": {
                                "status": "success",
                                "message": "Email validation successful",
                                "data": {
                                    "email": "valid.user@example.com",
                                    "deliverability": "DELIVERABLE",
                                    "is_valid_format": "TRUE"
                                }
                            }
                        },
                        "invalid_email": {
                            "value": {
                                "status": "success",
                                "message": "Email validation successful",
                                "data": {
                                    "email": "invalid.email@nonexistent.com",
                                    "deliverability": "UNDELIVERABLE",
                                    "is_valid_format": "TRUE"
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid email format",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid email format"
                    }
                }
            }
        },
        403: {
            "description": "Invalid API key",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid or missing API key"
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
                                "field": "query -> email",
                                "message": "field required",
                                "type": "missing"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "API rate limit exceeded",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "API rate limit exceeded. Please try again later."
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "An internal server error occurred"
                    }
                }
            }
        },
        502: {
            "description": "Invalid response from email validation service",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid response format from email validation service"
                    }
                }
            }
        },
        503: {
            "description": "Email validation service unavailable",
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Email validation service is temporarily unavailable"
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
                        "message": "Request to email validation service timed out"
                    }
                }
            }
        }
    }
)(check_email)