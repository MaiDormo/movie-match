from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.groq_controller import get_trivia_question, health_check
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter()

# Response Models
class BaseResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")

class TriviaResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    ai_question: str = Field(..., description="Generated trivia question for the movie")
    ai_response: int = Field(..., description="The correct answer (1, 2, or 3)")

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

router.get(
    "/",
    response_model=BaseResponse,
    summary="Health Check",
    description="Check if the GROQ API adapter service is running",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Service is healthy",
                            "value": {
                                "status": "success",
                                "message": "GROQ API adapter is up and running"
                            }
                        }
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Method not allowed"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal server error occurred"
                    }
                }
            }
        }
    }
)(health_check)

router.get(
    "/api/v1/get_trivia",
    response_model=TriviaResponse,
    summary="Get Movie Trivia",
    description="Generate a trivia question for a given movie using the GROQ API",
    responses={
        200: {
            "description": "Trivia question generated successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful trivia generation",
                            "value": {
                                "status": "success",
                                "message": "Trivia question generated successfully",
                                "ai_question": "In the film Titanic, what is the name of the ship's look-out who first spots the iceberg?\n1. Jack Dawson\n2. Frederick Fleet\n3. Cal Hockley\n",
                                "ai_answer": "2"
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Movie not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Movie not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "code": 422,
                        "message": "Request validation failed",
                        "details": [
                            {
                                "field": "query -> movie_title",
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
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "GROQ API error occurred"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "GROQ service is currently unavailable"
                    }
                }
            }
        },
        504: {
            "description": "Gateway timeout",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Request to GROQ API timed out"
                    }
                }
            }
        }
    }
)(get_trivia_question)