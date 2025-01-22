from fastapi import APIRouter
from controllers.tmdb_controller import discover_movies, get_movie_tmdb_id, get_movie, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/find-id", response_model=dict)(get_movie_tmdb_id)
router.get("/api/v1/discover-movies", response_model=dict)(discover_movies)
router.get("/api/v1/movie", response_model=dict)(get_movie)