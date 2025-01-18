from fastapi import APIRouter
from controllers.duckduckgo_controller import health_check, perform_image_search

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/get_image", response_model=dict)(perform_image_search)