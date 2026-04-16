from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, APIError, APITimeoutError, APIStatusError # Replaced Groq with AsyncOpenAI
import os
import json
from typing import Optional

from shared.common.response import create_response



class CerebrasSettings(BaseModel):
    """Configuration settings for Cerebras adapter"""
    api_key: Optional[str] = Field(default=os.getenv("CEREBRAS_API_KEY"), description="CEREBRAS API key from environment")
    base_url: str = Field(default="https://api.cerebras.ai/v1", description="Base URL for the provider")
    model_name: str = Field(default="llama3.1-8b", description="Model to use")

def get_settings() -> CerebrasSettings:
    """Dependency injection for Cerebras configuration"""
    return CerebrasSettings()


async def get_trivia_question(
        movie_title: str = Query(
        ..., 
        description="Movie title to generate trivia for",
        examples=["Titanic"],
        min_length=1,
        max_length=200
    ),
    settings: CerebrasSettings = Depends(get_settings)
) -> JSONResponse:
    """Generate a trivia question for a given movie based on model knowledge"""

    if not settings.api_key:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="CEREBRAS_API_KEY is not configured"
        )
    
    client = AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url
    )

    system_prompt = """You are a movie trivia expert API. Your only job is to generate a single, highly accurate trivia question based on the movie provided.
    RULES:
    1. Respond ONLY with a valid JSON object.
    2. Provide exactly 1 question, 3 options, and the exact string of the correct answer.
    3. If you do not recognize the movie, set "success" to false.
    
    SCHEMA:
    {
        "success": true,
        "question": "...",
        "options": ["A", "B", "C"],
        "correct_answer": "A",
        "error_message": null
    }"""

    try:


        response = await client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a trivia question for the movie: '{movie_title}'"}
            ],
            response_format={"type": "json_object"}, # Forces guaranteed JSON
            temperature=0.7 
        )

        if not response.choices:
            return create_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message="LLM returned an empty response"
            )

        raw_content = response.choices[0].message.content
        if not raw_content:
            return create_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message="LLM returned no message content"
            )

        trivia_data = json.loads(raw_content)

        required_fields = ["question", "options", "correct_answer"]
        if trivia_data.get("success", True) and any(field not in trivia_data for field in required_fields):
            return create_response(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message="LLM response did not match expected schema"
            )

        if not trivia_data.get("success", True):
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message=trivia_data.get("error_message", "Movie not recognized by AI.")
            )

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Trivia question generated successfully",
            data={
                "question": trivia_data["question"],
                "options": trivia_data["options"],
                "correct_answer": trivia_data["correct_answer"]
            }
        )
    
    except APIStatusError as e:
        return create_response(
            status_code=e.status_code if e.status_code else status.HTTP_502_BAD_GATEWAY,
            message="LLM API returned an HTTP status error"
        )

    except APITimeoutError:
        return create_response(status_code=status.HTTP_504_GATEWAY_TIMEOUT, message="LLM API timed out")
    except APIError as e:
        return create_response(status_code=status.HTTP_502_BAD_GATEWAY, message=f"LLM API Error: {str(e)}")
    except json.JSONDecodeError:
        return create_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="AI returned invalid JSON")
    except Exception:
        return create_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unexpected internal error")
