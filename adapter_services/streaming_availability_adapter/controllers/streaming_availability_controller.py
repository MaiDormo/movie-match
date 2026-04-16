from fastapi import Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from typing import Any, Optional
import os

from shared.common.http_utils import make_request
from shared.common.response import create_response

class StreamAvailSettings(BaseModel):
    """Streaming Availability API configuration Settings"""
    stream_avail_url: str = "https://streaming-availability.p.rapidapi.com/shows"
    stream_avail_api_key: Optional[str] = os.getenv("STREAMING_AVAILABILITY_API_KEY")
    stream_avail_host: str = "streaming-availability.p.rapidapi.com"

def get_settings() -> StreamAvailSettings:
    """Dependency Injection for Streaming Availability"""
    return StreamAvailSettings()


def _filter_data(stream_avail_data: dict[str, Any], country: str) -> list[dict[str,Any]]:
    """Filter and extract relevant streaming availability data."""
    # Check if we have valid streaming options for the country
    if not stream_avail_data or 'streamingOptions' not in stream_avail_data or not stream_avail_data['streamingOptions']:
        return []  # Return empty list if no streaming options available

    streaming_options = stream_avail_data['streamingOptions'].get(country, [])
    if not streaming_options:
        return []  # Return empty list if no options for this country

    service_dict: dict[str, dict[str, Any]] = {}  # Dictionary to track unique services
    
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
    result: list[dict[str, Any]] = []
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


def _fetch_streaming_data(
        imdb_id: str, country: str, settings: StreamAvailSettings
) -> dict[str, Any]:
    """fetch raw payload from Streaming Availability API"""
    headers = {
        "x-rapidapi-key": settings.stream_avail_api_key,
        "x-rapidapi-host": settings.stream_avail_host,
    }

    url = f"{settings.stream_avail_url}/{imdb_id}"
    params = {"country": country}

    return make_request(url=url, headers=headers, params=params)

async def get_movie_availability(
    imdb_id: str = Query(
        ...,
        description="IMDB ID of the movie",
        examples=["tt0120338"],
        pattern="^tt[0-9]{7,8}$"
    ),
    country: str = Query(
        ...,
        description="Two-letter country code (ISO 3166-1 alpha-2 (lowercase))",
        examples=["us"],
        min_length=2,
        max_length=2,
        pattern="^[a-z]{2}$"
    ),
    settings: StreamAvailSettings = Depends(get_settings)
) -> JSONResponse:
    
    try:
        raw_data = _fetch_streaming_data(imdb_id,country,settings)
        services = _filter_data(raw_data, country)

        if not services:
            return create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="No Streaming services found for this movie",
            )
        
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Streaming services retrieved successfully",
            data={"services": services},
        )

    except HTTPError as e:
        if e.response.status_code == 429:
            return create_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message="Streaming Availability API rate limit exceeded"
            )
        elif e.response.status_code == 401:
            return create_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid Streaming Availability API credentials"
            )
        return create_response(
            status_code=e.response.status_code,
            message=f"Streaming Availability API error: {str(e)}"
        )
    except ConnectionError:
        return create_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message="Streaming Availability service is currently unavailable"
        )
    
    except Timeout:
        return create_response(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            message="Request to Streaming Availabiltiy API timed out"
        )
    
    except RequestException as e:
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to connect to Streaming Availability API: {str(e)}"
        )



    