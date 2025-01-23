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
    ai_response: int = Field(..., description="The correct answer to the respone can be of value [1,2,3]")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Trivia question generated successfully",
                "ai_question": "In the film Titanic, what is the name of the ship's look-out who first spots the iceberg?\n1. Jack Dawson\n2. Frederick Fleet\n3. Cal Hockley\n",
                "ai_answer": "2"
            }
        }

class ValidationError(BaseModel):
    field: str
    message: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "field": "query -> movie_title",
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
                        "field": "query -> movie_title",
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
    description="Check if the GROQ API adapter service is running",
    responses={
        200: {"description": "Service is running", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        500: {"description": "Internal server error", "model": BaseResponse}
    }
)(health_check)

router.get(
    "/api/v1/get_trivia",
    response_model=TriviaResponse,
    summary="Get Movie Trivia",
    description="Generate a trivia question for a given movie using the GROQ API",
    responses={
        200: {"description": "Trivia question generated successfully", "model": TriviaResponse},
        404: {"description": "HTTP error occured: [message inserted]", "model": BaseResponse},
        405: {"description": "The HTTP method is not allowed for this endpoint", "model": BaseResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error or GROQ API error", "model": BaseResponse},
        503: {"description": "GROQ service unavailable", "model": BaseResponse},
        504: {"description": "GRQPRequest to GROQ API timed out", "model": BaseResponse}
    }
)(get_trivia_question)