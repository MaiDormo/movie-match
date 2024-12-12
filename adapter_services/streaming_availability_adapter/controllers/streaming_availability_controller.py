from flask import jsonify, request
import os
import requests

streaming_availability_url = "https://streaming-availability.p.rapidapi.com/shows/search/title"
streaming_availability_api_key = os.getenv("STREAMING_AVAILABILITY_API_KEY")
streaming_availability_host = "streaming-availability.p.rapidapi.com"

def handle_error(e, status_code, message):
    response = {
        "status": "error",
        "code": status_code,
        "message": message,
        "error": str(e) if e else None
    }
    return jsonify(response), status_code

def filter_data(streaming_availability_data, country):
    if streaming_availability_data and 'streamingOptions' in streaming_availability_data[0] and country in streaming_availability_data[0]['streamingOptions']:
        streaming_options = streaming_availability_data[0]['streamingOptions'][country]
        return [
            {
                "service_name": stream_opts.get("service", {}).get("name", "Unknown"),
                "service_type": stream_opts.get("type", "Unknown"),
                "quality": stream_opts.get("quality", "Unknown")
            }
            for stream_opts in streaming_options
        ]
    return None

def get_movie_availability():
    title = request.args.get("title")
    country = request.args.get("country")

    if not title:
        return handle_error(None, 400, "Movie title is required")
    
    if not country:
        return handle_error(None, 400, "Country is required")
    
    headers = {
        "x-rapidapi-key": streaming_availability_api_key,
        "x-rapidapi-host": streaming_availability_host
    }

    params = {
        "country": country,
        "title": title
    }

    try:
        response = requests.get(streaming_availability_url, headers=headers, params=params)
        response.raise_for_status()
        streaming_availability_data = response.json()

        if 'Error' in streaming_availability_data:
            return handle_error(None, 404, streaming_availability_data['Error'])
        
        result = filter_data(streaming_availability_data, country)
        
        if result:
            return jsonify({"status": "success", "data": result})
        else:
            return handle_error(None, 404, "No streaming options found for the specified country")
        
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the Streaming Availability API")

def health_check():
    response = {
        "status": "success",
        "message": "STREAMING AVAILABILITY API Adapter is up and running!"
    }
    return jsonify(response), 200