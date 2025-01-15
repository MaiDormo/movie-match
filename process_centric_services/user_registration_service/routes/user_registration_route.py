from fastapi import APIRouter
from controllers.user_registration_controller import health_check, registrate_user

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.post("/api/v1/registrate-user", response_model=dict)(registrate_user)