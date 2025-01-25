from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.valid_email_controllers import health_check, validate_email
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class BaseResponseWithData(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data or error details")

# Router endpoints
router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the Email Validation Service is running",
    responses={
        200: {
            "description": "Service is running", 
            "model": BaseResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Valid Email Business Logic Service is up and running"
                    }
                }
            }
        },
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/validate-email",
    response_model=BaseResponseWithData,
    summary="Validate Email Address",
    description="Validate an email address format and its deliverability.",
    responses={
        200: {
            "description": "Email validation successful",
            "model": BaseResponseWithData,
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Email validation successful",
                        "data": {
                            "email_check": {
                            "email": "a@gmaiul.com",
                            "valid": "true",
                            "message": "Email validation successful"
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Invalid email format or undeliverable email",
            "model": BaseResponseWithData,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Email validation failed",
                        "data": {
                            "email": "Invalid email format. Please provide a valid email address."
                        }
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
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
        500: {
            "description": "Internal server error",
            "model": BaseResponse
        }
    }
)(validate_email)