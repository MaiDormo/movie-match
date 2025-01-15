from fastapi import APIRouter
from controllers.groq_controller import get_trivia_question, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/get_trivia", response_model=dict)(get_trivia_question)