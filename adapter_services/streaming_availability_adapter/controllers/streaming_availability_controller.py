from fastapi import Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
import requests

class Settings(BaseModel):
    stream_avail_url: str = "https://streaming-availability.p.rapidapi.com/shows"
    stream_avail_api_key: str = os.getenv("STREAMING_AVAILABILITY_API_KEY")
    stream_avail_host: str = "streaming-availability.p.rapidapi.com"

def get_settings():
    return Settings()

def create_response(status_code: int, message: str, data: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized API response"""
    content = {
        "status": "success" if status_code < 400 else "error",
        "message": message
    }
    if data:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def filter_data(stream_avail_data, country):
    """Filter and extract relevant streaming availability data."""
    # Check if we have valid streaming options for the country
    if not stream_avail_data or 'streamingOptions' not in stream_avail_data or not stream_avail_data['streamingOptions']:
        return []  # Return empty list if no streaming options available

    streaming_options = stream_avail_data['streamingOptions'].get(country, [])
    if not streaming_options:
        return []  # Return empty list if no options for this country

    service_dict = {}  # Dictionary to track unique services
    
    for stream_opts in streaming_options:
        service_name = stream_opts.get("service", {}).get("name", "Unknown")
        service_type = stream_opts.get("type", "Unknown")
        link = stream_opts.get("link", "Unknown")
        logo = stream_opts.get("service", {}).get("imageSet", {}).get("lightThemeImage", None)
        
        # Capitalize the first letter of service_type
        service_type = service_type.capitalize()
        
        # If the service hasn't been added yet, add it
        if service_name not in service_dict:
            service_dict[service_name] = {
                "service_name": service_name,
                "links": [link],
                "logos": [logo],
                "service_types": [service_type]
            }
        else:
            # Add the link, logo, and service_type to existing ones
            existing_service = service_dict[service_name]
            existing_service["links"].append(link)
            existing_service["logos"].append(logo)
            existing_service["service_types"].append(service_type)

    # Update each service with the final type (sorted and concatenated)
    result = []
    for service_name, service_data in service_dict.items():
        sorted_service_types = sorted(set(service_data["service_types"]))
        result.append({
            "service_name": service_name,
            "service_type": "/".join(sorted_service_types),
            "link": service_data["links"][0],  # Keep only first link
            "logo": service_data["logos"][0]   # Keep only first logo
        })

    # Create a sorted list by service_name
    return sorted(result, key=lambda x: x['service_name'])

def make_request(url, headers, params, country):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        filtered_response = filter_data(response.json(), country)
        if 'Error' in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response['Error']
            )
        return filtered_response
    except requests.exceptions.HTTPError as e:
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message="HTTP error occurred",
            data={"error": str(e)}
        )
    except requests.exceptions.ConnectionError as e:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Connection error occurred",
            data={"error": str(e)}
        )
    except requests.exceptions.Timeout as e:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request timed out",
            data={"error": str(e)}
        )
    except requests.exceptions.RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while calling the Streaming Availability API",
            data={"error": str(e)}
        )
    

async def get_movie_availability(
    imdb_id: str = Query(...),
    country: str = Query(...),
    settings: Settings = Depends(get_settings)
):
    if not imdb_id or not country:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IMDB ID and country are required"
        )

    headers = {
        "x-rapidapi-key": settings.stream_avail_api_key,
        "x-rapidapi-host": settings.stream_avail_host
    }
    url = f"{settings.stream_avail_url}/{imdb_id}"  # Updated endpoint with imdb_id in the path
    params = {"country": country}  # Only country is needed as a query parameter

    result = make_request(url, headers, params, country)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Streaming availability retrieved successfully",
        data=result
    )
    

async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return create_response(
        status_code=status.HTTP_200_OK,
        message="STREAMING AVAILABILITY API Adapter is up and running!"
    )