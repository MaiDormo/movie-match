from fastapi import APIRouter
from controllers.tmdb_controller import discover_movies, get_movie_popularity, get_movie_popularity_id, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/search", response_model=dict)(get_movie_popularity)
router.get("/api/v1/find", response_model=dict)(get_movie_popularity_id)
router.get("/api/v1/discover-movies", response_model=dict)(discover_movies)