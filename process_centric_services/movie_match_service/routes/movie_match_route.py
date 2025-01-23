from fastapi import APIRouter
from controllers.movie_match_controller import health_check, get_movie_details, get_user_genres, get_movie_search_by_text, get_genre_movie_search_by_url

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/movies", response_model=dict)(get_movie_details)

router.get("/api/v1/user-genres", response_model=dict)(get_user_genres)
# router.put("/api/v1/user-genres/update", response_model=dict)(update_user_genres)

router.get("/api/v1/movies/search-by-text", response_model=dict)(get_movie_search_by_text)
router.get("/api/v1/movies/search-by-genre", response_model=dict)(get_genre_movie_search_by_url)


