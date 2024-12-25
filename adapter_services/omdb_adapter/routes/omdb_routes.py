from fastapi import APIRouter
from controllers.omdb_controller import get_movie_id, get_movies, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/search", response_model=dict)(get_movies)
router.get("/api/v1/find", response_model=dict)(get_movie_id)