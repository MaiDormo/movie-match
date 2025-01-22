from fastapi import APIRouter
from controllers.movie_details_controller import get_movie_details, health_check


router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/movie_details", response_model=dict)(get_movie_details)