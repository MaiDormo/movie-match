from fastapi import APIRouter
from controllers.streaming_availability_controller import get_movie_availability, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/avail", response_model=dict)(get_movie_availability)
