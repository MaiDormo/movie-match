from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import Annotated, Optional, Dict, Any
import requests
import jwt
from datetime import datetime, timedelta
import pytz

# Constants
MOVIE_DETAILS_URL = "http://movie-details-service:5000/api/v1/movie_details"

MOVIE_SEARCH_GET_GENRES_URL = "http://movie-search-service:5000/api/v1/user_genres"
MOVIE_SEARCH_SET_GENRES_URL = "http://movie-search-service:5000/api/v1/update_user_genres"
MOVIE_SEARCH_BY_TEXT_URL = "http://movie-search-service:5000/api/v1/movie_search_text"
MOVIE_SEARCH_BY_GENRE_URL = "http://movie-search-service:5000/api/v1/movie_search_genre"

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def handle_service_request(method: str, url: str, **kwargs) -> Dict:
    """Handle external service requests with standardized error handling"""
    try:
        # Log dell'endpoint e dei parametri
        print(f"Calling endpoint: {url}")
        print(f"Request method: {method}")
        print(f"Request parameters: {kwargs}")

        if method.lower() == "get":
            response = requests.get(url, **kwargs)
        elif method.lower() == "post":
            response = requests.post(url, **kwargs)
        elif method.lower() == "put":
            response = requests.put(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        # Try to get detailed error message from response
        try:
            error_data = response.json()
            error_detail = error_data.get('detail') or error_data.get('message')
            if error_data.get('data'):
                return error_data  # Return the error response directly for validation errors
            return create_response(
                status_code=response.status_code,
                message=error_detail or str(http_err)
            )
        except ValueError:
            return create_response(
                status_code=response.status_code,
                message=str(http_err)
            )
            
    except requests.exceptions.ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Service is temporarily unavailable. Please try again later."
        )
    except requests.exceptions.Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request timed out. Please try again."
        )
    except requests.exceptions.RequestException as req_err:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An error occurred while processing your request: {req_err}"
        )
    except ValueError as val_err:
        return create_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=f"Invalid data format: {val_err}"
        )

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Movie Match Service is up and running!"
    )

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict
import requests

# Router definition
router = APIRouter()

async def get_movie_details(id: str) -> JSONResponse:
    """Fetch movie details by ID."""
    try:
        # Construct the service URL
        params = {"movie_id": id}

        # Request movie details from the service
        movie_details = handle_service_request(
            method="get",
            url=MOVIE_DETAILS_URL,
            params=params
        )

        # Check for errors in the service response
        if movie_details.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=movie_details.get("message", "Failed to fetch movie details"),
                data=movie_details.get("data") or {"detail": movie_details.get("detail", "Unknown error")}
            )

        # Return the fetched movie details
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movie details fetched successfully",
            data=movie_details.get("data")
        )

    except HTTPException as http_err:
        raise http_err  # Propagate FastAPI exceptions

    except Exception as e:
        # Handle unexpected errors
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred : {str(e)}"
        )

async def get_user_genres(user_id: str) -> JSONResponse:
    """Fetch user genres based on user ID."""
    try:
        # Construct the service URL
        params = {"user_id": user_id}
        
        # Request user genres from the service
        user_genres = handle_service_request(
            method="get",
            url=MOVIE_SEARCH_GET_GENRES_URL,
            params=params
        )

        # Check for errors in the service response
        if user_genres.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=user_genres.get("message", "Failed to fetch user genres"),
                data=user_genres.get("data") or {"detail": user_genres.get("detail", "Unknown error")}
            )

        # Return the fetched user genres
        return create_response(
            status_code=status.HTTP_200_OK,
            message="User genres fetched successfully",
            data=user_genres.get("data")
        )

    except HTTPException as http_err:
        raise http_err  # Propagate FastAPI exceptions

    except Exception as e:
        # Handle unexpected errors
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred: {str(e)}"
        )
    

# async def update_user_genres(
#     user_id: str,
#     preferences: list[int]
# ) -> JSONResponse:
#     """Update user genres preferences based on user ID."""
#     try:
#         print("ciao")
#         # Costruisci l'URL del servizio
#         url = MOVIE_SEARCH_SET_GENRES_URL
#         data = {
#             "id": user_id,  # Passa l'id nel corpo della richiesta
#             "preferences": preferences
#         }

#         # Richiesta PUT per aggiornare le preferenze dell'utente
#         response = handle_service_request(
#             method="put",
#             url=url,
#             json=data
#         )

#         # Se la risposta contiene un errore, restituisci una risposta con l'errore
#         if response.get("status") == "error":
#             return create_response(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 message=response.get("message", "Failed to update user preferences"),
#                 data=response.get("data") or {"detail": response.get("detail", "Unknown error")}
#             )

#         # Restituisci una risposta di successo con i dati aggiornati
#         return create_response(
#             status_code=status.HTTP_200_OK,
#             message="User preferences updated successfully",
#             data=response
#         )

#     except HTTPException as http_err:
#         raise http_err  # Propaga le eccezioni di FastAPI

#     except Exception as e:
#         # Gestisci errori inaspettati
#         return create_response(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             message=f"An unexpected error occurred: {str(e)}"
#         )

async def get_movie_search_by_text(
    query: str 
) -> JSONResponse:
    """
    Esegue una ricerca di film basata su una query di testo.

    Args:
        query (str): La query di testo per la ricerca dei film.
        settings (Settings): Iniezione delle impostazioni di configurazione per gli endpoint esterni.

    Returns:
        JSONResponse: Una risposta API standardizzata che contiene il risultato della ricerca.
    """
    try:

        # Parametri della richiesta
        params = {"query": query}

        # Request user genres from the service
        movie_list = handle_service_request(
            method="get",
            url=MOVIE_SEARCH_BY_TEXT_URL,
            params=params
        )
        # Check for errors in the service response
        if movie_list.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=movie_list.get("message", "Failed to fetch movies"),
                data=movie_list.get("data") or {"detail": movie_list.get("detail", "Unknown error")}
            )

        # Return the fetched user genres
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies fetched successfully",
            data=movie_list.get("data")
        )

    except HTTPException as http_err:
        raise http_err  # Propagate FastAPI exceptions

    except Exception as e:
        # Handle unexpected errors
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred: {str(e)}"
        )

async def get_genre_movie_search_by_url(
    with_genres: str
) -> JSONResponse:
    try:
        # Costruzione dei parametri per la richiesta
        params = {
            "language": "en-EN",
            "with_genres": with_genres,
            "vote_avg_gt": 8.0,
            "sort_by": "popularity.desc"
        }

        # Request user genres from the service
        movie_list = handle_service_request(
            method="get",
            url=MOVIE_SEARCH_BY_GENRE_URL,
            params=params
        )
        # Check for errors in the service response
        if movie_list.get("status") == "error":
            return create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=movie_list.get("message", "Failed to fetch movies"),
                data=movie_list.get("data") or {"detail": movie_list.get("detail", "Unknown error")}
            )

        # Return the fetched user genres
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies fetched successfully",
            data=movie_list.get("data")
        )

    except HTTPException as http_err:
        raise http_err  # Propagate FastAPI exceptions

    except Exception as e:
        # Handle unexpected errors
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred: {str(e)}"
        )