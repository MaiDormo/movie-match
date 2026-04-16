from fastapi import APIRouter
from controllers.llm_controller import get_trivia_question
from pydantic import BaseModel, Field
from typing import Any

router = APIRouter()


class TriviaData(BaseModel):
    question: str = Field(..., description="Generated trivia question for the movie")
    options: list[str] = Field(..., description="Three multiple-choice options")
    correct_answer: str = Field(..., description="Correct answer text")


class TriviaResponse(BaseModel):
    status: str = Field(..., description="Response status ('success' or 'error')")
    message: str = Field(..., description="Response message")
    data: TriviaData | None = Field(default=None, description="Trivia payload for successful responses")


SUCCESS_TRIVIA_EXAMPLE: dict[str, Any] = {
    "status": "success",
    "message": "Trivia question generated successfully",
    "data": {
        "question": "Who directed this movie?",
        "options": ["Option A", "Option B", "Option C"],
        "correct_answer": "Option B",
    },
}

ERROR_EXAMPLES: dict[int, dict[str, Any]] = {
    404: {"status": "error", "message": "Movie not recognized by AI."},
    500: {"status": "error", "message": "Invalid JSON / Unexpected internal Error"},
    502: {"status": "error", "message": "LLM API Error: example_error"},
    504: {"status": "error", "message": "LLM API timed out"},
}

RESPONSE_DESCRIPTIONS: dict[int, str] = {
    200: "Success",
    502: "Bad gateway",
    404: "Not found",
    405: "Method not allowed",
    422: "Validation error",
    500: "Internal server error",
    503: "LLM API unavailable",
    504: "Gateway timeout",
}

TRIVIA_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": RESPONSE_DESCRIPTIONS[200],
        "content": {
            "application/json": {
                "examples": {
                    "success": {
                        "summary": "Movies found",
                        "value": SUCCESS_TRIVIA_EXAMPLE,
                    }
                }
            }
        },
    }
}

for status_code, example in ERROR_EXAMPLES.items():
    TRIVIA_RESPONSES[status_code] = {
        "description": RESPONSE_DESCRIPTIONS[status_code],
        "content": {"application/json": {"example": example}},
    }


router.add_api_route(
    "/api/v1/get_trivia",
    endpoint=get_trivia_question,
    response_model=TriviaResponse,
    summary="Get Movie Trivia",
    description="Generate a trivia question for a given movie using the LLM API",
    responses=TRIVIA_RESPONSES,
    methods=["GET"],
)



