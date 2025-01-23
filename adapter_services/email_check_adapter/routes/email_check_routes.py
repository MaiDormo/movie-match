from fastapi import APIRouter
from controllers.email_check_controller import health_check, check_email
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

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
                    "deliverability": "UNDELIVERABLE",
                    "is_valid_format": "TRUE"
                }
            }
        }

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> email",
                "message": "field required",
                "type": "missing"
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

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
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)(health_check)

router.get(
    "/api/v1/email",
    response_model=EmailValidationResponse,
    summary="Validate Email",
    description="Validate an email address using the Abstract Email Validation API",
    responses={
        200: {"description": "Email validation completed successfully", "model": EmailValidationResponse},
        400: {"description": "Invalid email format", "model": BaseResponse},
        403: {"description": "Invalid API key", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        429: {"description": "API rate limit exceeded", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse},
        502: {"description": "Invalid response from email validation service", "model": BaseResponse},
        503: {"description": "Email validation service is temporarily unavailable", "model": BaseResponse},
        504: {"description": "Request to email validation service timed out", "model": BaseResponse}
    }
)(check_email)