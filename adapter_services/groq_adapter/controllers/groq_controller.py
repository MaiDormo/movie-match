from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from groq import Groq
import os
from typing import Dict, Any
import requests

class Settings(BaseModel):
    """Configuration settings for GROQ adapter"""
    groq_url: str = ""
    groq_api_key: str = Field(default=os.getenv("GROQ_API_KEY"), description="GROQ API key from environment")

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content.update(data)
    return JSONResponse(content=content, status_code=status_code)

async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="GROQ API Adapter is up and running!"
    )

async def get_trivia_question(
    movie_title: str = Query(
        ..., 
        description="Movie title to generate trivia for",
        example="Titanic",
        min_length=1,
        max_length=200
    ),
    settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """Generate a trivia question for a given movie"""
    
    # Validate API key
    if not settings.groq_api_key:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="GROQ_API_KEY environment variable is not set"
        )

    try:
        # Initialize GROQ client
        client = Groq(api_key=settings.groq_api_key)
        
        # Prepare AI prompt
        prompt = (
            "Ask a trivia question about this film, give 3 answer options, "
            "end with the correct answer number (1, 2, or 3).\n"
            f"Film: {movie_title}"
        )

        # Make API request
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="llama-3.3-70b-versatile",
            temperature=1.5,
            max_tokens=130
        )

        # Extract question and answer
        response_text = chat_completion.choices[0].message.content
        question = response_text[:-1]  # Everything except last character
        answer = response_text[-1]    # Only last character

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Trivia question generated successfully",
            data={
                "ai_question": question,
                "ai_answer": answer
            }
        )

    except requests.exceptions.HTTPError as e:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"HTTP error occurred: {str(e)}"
        )
    except requests.exceptions.ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="GROQ API is currently unavailable"
        )
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to GROQ API timed out"
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling GROQ API: {str(e)}"
        )
    except Exception as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}"
        )