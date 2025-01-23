from fastapi import APIRouter
from controllers.movie_search_controller import get_user_genres, get_text_movie_search, update_user_preferences, get_genre_movie_search, health_check


router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/user_genres", response_model=dict)(get_user_genres)
router.put("/api/v1/update_user_genres", response_model=dict)(update_user_preferences)

router.get("/api/v1/movie_search_text", response_model=dict)(get_text_movie_search)
router.get("/api/v1/movie_search_genre", response_model=dict)(get_genre_movie_search)