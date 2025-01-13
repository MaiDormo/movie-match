from fastapi import APIRouter
from controllers.email_check_controller import health_check, check_email

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/email", response_model=dict)(check_email)