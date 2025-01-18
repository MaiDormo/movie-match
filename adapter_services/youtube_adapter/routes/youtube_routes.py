from fastapi import APIRouter
from controllers.youtube_controller import health_check, search_youtube

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/get_video", response_model=dict)(search_youtube)