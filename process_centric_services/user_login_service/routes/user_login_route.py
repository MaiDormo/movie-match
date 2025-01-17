from fastapi import APIRouter
from controllers.user_login_controller import health_check, login, refresh_token

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.post("/api/v1/login", response_model=dict)(login)
router.post("/api/v1/refresh-token", response_model=dict)(refresh_token)


