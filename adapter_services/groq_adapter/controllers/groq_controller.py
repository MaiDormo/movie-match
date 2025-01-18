from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from groq import Groq
import os
import requests

class Settings(BaseModel):
    groq_url: str = ""
    groq_api_key: str = os.getenv("GROQ_API_KEY")

def get_settings():
    return Settings()

def handle_error(e, status_code, message):
    response = {
        "status": "error",
        "code": status_code,
        "message": message,
        "error": str(e)
    }
    return JSONResponse(content=response, status_code=status_code)

def make_request(url, params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def health_check():
    response = {
        "status": "success",
        "message": "GROQ API Adapter is up and running!"
    }
    return JSONResponse(content=response, status_code=200)

async def get_trivia_question(movie_title: str = Query(...),settings: Settings = Depends(get_settings)):
    # Recupera l'API key dalle variabili d'ambiente
    api_key = settings.groq_api_key
    if not api_key:
        return JSONResponse(
            content={"status": "error", "message": "La variabile d'ambiente 'GROQ_API_KEY' non è impostata."},
            status_code=400
        )

    # Inizializza il client Groq
    client = Groq(api_key=api_key)
    message_to_ai = "Ask a trivia question about this film, give 3 answer options, end with the correct answer number (1, 2, or 3).\nFilm: " + movie_title
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message_to_ai,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=1.5,
            max_tokens=130
        )
        question = chat_completion.choices[0].message.content[:-1]  # tutto tranne l'ultimo carattere
        answer = chat_completion.choices[0].message.content[-1]   # solo l'ultimo carattere

        response = {
            "status": "success",
            "ai_question": question,
            "ai_answer": answer
        }
        return JSONResponse(content=response, status_code=200)

        
    # Gestione degli errori HTTP
    except requests.exceptions.HTTPError as e:
        return JSONResponse(
            content={"status": "error", "message": f"HTTP error occurred: {str(e)}"},
            status_code=404
        )
    except requests.exceptions.ConnectionError as e:
        return JSONResponse(
            content={"status": "error", "message": "Connection error occurred"},
            status_code=503
        )
    except requests.exceptions.Timeout as e:
        return JSONResponse(
            content={"status": "error", "message": "Request timed out"},
            status_code=504
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"status": "error", "message": f"An error occurred while calling the GROQ API: {str(e)}"},
            status_code=500
        )
