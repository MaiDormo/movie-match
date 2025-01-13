from fastapi import APIRouter
from controllers.valid_email_controllers import health_check, validate_email

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/validate-email", response_model=dict)(validate_email)