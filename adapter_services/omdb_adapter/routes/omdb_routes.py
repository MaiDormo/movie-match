from fastapi import APIRouter, Depends
from controllers.omdb_controller import get_movie_id, get_movies, health_check, MovieQuery, MovieIDQuery

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/movies", response_model=dict)(get_movies)
router.get("/api/v1/movie", response_model=dict)(get_movie_id)