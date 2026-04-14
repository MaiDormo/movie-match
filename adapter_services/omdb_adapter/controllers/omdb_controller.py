import json
import os
from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from typing import Optional

from shared.common.response import create_response
from shared.common.http_utils import make_request


def _response_payload(response: JSONResponse) -> dict:
    return json.loads(bytes(response.body))


class OMDBSettings(BaseModel):
    """Configuration settings for OMDB adapter"""
    omdb_url: str = Field(default="http://www.omdbapi.com/", description="OMDB API base URL")
    omdb_api_key: Optional[str] = Field(default=os.getenv("OMDB_API_KEY"), description="OMDB API key from environment")

def get_settings() -> OMDBSettings:
    """Dependency injection for OMDB configuration"""
    return OMDBSettings()



async def get_movie_id(
    id: str = Query(..., description="IMDB movie ID"),
    settings: OMDBSettings = Depends(get_settings)
) -> JSONResponse:
    """
    Get movie details by IMDB ID and filter response to match Movie schema
    """
    params = {
        "apikey": settings.omdb_api_key,
        "i": id,
    }
    
    try:
        movie_data = make_request(settings.omdb_url, params=params)
        
        # Filter data
        filtered_data = {
            "Title": movie_data.get("Title", "N/A"),
            "Year": movie_data.get("Year", "N/A"),
            "imdbID": movie_data.get("imdbID", "N/A"), 
            "Type": movie_data.get("Type", "movie"),
            "Director": movie_data.get("Director", "N/A"),
            "Genre": movie_data.get("Genre", "N/A"),
            "Poster": movie_data.get("Poster", "N/A"),
            "imdbRating": movie_data.get("imdbRating", "N/A")
        }

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movie details retrieved successfully",
            data=filtered_data
        )
    
    except HTTPError as e:
        error_msg = f"HTTP error occured: {str(e)}"
        
        return create_response(
            status_code=e.response.status_code,
            message=error_msg
        )
    
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="OMDB API is currently unavailable"
        )

    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to OMDB API timed out"
        ) 

    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling OMDB API: {str(e)}"
        )




async def get_movies_with_info(
    title: str = Query(..., description="Movie title to search for"),
    settings: OMDBSettings = Depends(get_settings)
) -> JSONResponse:
    """Search movies and include additional details"""
    
    params = {
        "apikey": settings.omdb_api_key,
        "s": title,
        "type": "movie"
    }

    try:    
        # Get initial movie list
        movies = make_request(settings.omdb_url, params=params)

        films_list = movies.get("Search", [])
        
        # Get detailed information for each movie
        detailed_movies = []
        for movie in films_list:
            movie_details_response = await get_movie_id(id=movie["imdbID"], settings=settings)
            
            movie_details = _response_payload(movie_details_response)
            
            if movie_details["status"] == "success":
                movie_data = movie_details["data"]
                detailed_movies.append({
                    **movie,
                    "Genre": movie_data.get("Genre", "N/A"),
                    "imdbRating": movie_data.get("imdbRating", "N/A")
                })

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Movies retrieved successfully",
            data={"movies": detailed_movies}
        )
    
    except HTTPError as e:
        error_msg = f"HTTP error occured: {str(e)}"
        
        return create_response(
            status_code=e.response.status_code,
            message=error_msg
        )
    
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="OMDB API is currently unavailable"
        )

    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to OMDB API timed out"
        ) 

    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error calling OMDB API: {str(e)}"
        )