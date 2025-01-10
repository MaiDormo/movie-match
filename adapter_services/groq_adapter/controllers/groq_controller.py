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

async def print_statement(settings: Settings = Depends(get_settings)):
    # Recupera l'API key dalle variabili d'ambiente
    api_key = settings.groq_api_key
    if not api_key:
        return JSONResponse(
            content={"status": "error", "message": "La variabile d'ambiente 'GROQ_API_KEY' non è impostata."},
            status_code=400
        )

    # Inizializza il client Groq
    client = Groq(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Print numbers from 1 to 10",
                }
            ],
            model="llama-3.3-70b-versatile"
        )

        response = {
            "status": "success",
            "message": chat_completion.choices[0].message.content
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
    message_to_ai = "Stampa il seguente messaggio e infine stampa come ultimo carattere una cifra randomica tra 1 e 3: " + movie_title
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message_to_ai,
                }
            ],
            model="llama-3.3-70b-versatile"
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



def main():
    # Recupera l'API key dalle variabili d'ambiente
    api_key = "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"
    if not api_key:
        print("Errore: La variabile d'ambiente 'GROQ_API_KEY' non è impostata.")
        return

    # Inizializza il client Groq
    client = Groq(api_key=api_key)

    # Esegui una richiesta per completare la chat
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Print numbers from 1 to 10",
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        # Stampa il risultato
        print("Risultato completamento:")
        print(chat_completion.choices[0].message.content)

    except Exception as e:
        print("Errore durante la chiamata al servizio Groq:", e)

if __name__ == "__main__":
    main()