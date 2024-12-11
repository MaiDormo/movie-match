from flask import jsonify, request
import os
import requests

omdbUrl = "http://www.omdbapi.com/"
omdbAPIKey = os.getenv("OMDB_API_KEY")

def handle_error(e, status_code, message):
    response = {
        "status": "error",
        "code": status_code,
        "message": message,
        "error": str(e)
    }
    return jsonify(response), status_code

def get_movies():
    t = request.args.get("t")
    
    if t is None:
        response = {
            "status": "fail",
            "message": "Movie title is required"
        }
        return jsonify(response), 400

    params = {
        "apikey": omdbAPIKey,
        "t": t,
    }
    
    try:
        response = requests.get(omdbUrl, params=params)
        response.raise_for_status()
        movies = response.json()
        
        if 'Error' in movies:
            response = {
                "status": "fail",
                "message": movies['Error']
            }
            return jsonify(response), 404
        
        return jsonify(movies)
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")

def get_movie_id():
    i = request.args.get("i")
    
    if i is None:
        response = {
            "status": "fail",
            "message": "Movie ID is required"
        }
        return jsonify(response), 400

    params = {
        "apikey": omdbAPIKey,
        "i": i,
    }
    
    try:
        response = requests.get(omdbUrl, params=params)
        response.raise_for_status()
        movie = response.json()
        
        if 'Error' in movie:
            response = {
                "status": "fail",
                "message": movie['Error']
            }
            return jsonify(response), 404
        
        return jsonify(movie)
    except requests.exceptions.HTTPError as e:
        return handle_error(e, response.status_code, "HTTP error occurred")
    except requests.exceptions.ConnectionError as e:
        return handle_error(e, 503, "Connection error occurred")
    except requests.exceptions.Timeout as e:
        return handle_error(e, 504, "Request timed out")
    except requests.exceptions.RequestException as e:
        return handle_error(e, 500, "An error occurred while calling the OMDB API")

def health_check():
    response = {
        "status": "success",
        "message": "OMDB API Adapter is up and running!"
    }
    return jsonify(response), 200