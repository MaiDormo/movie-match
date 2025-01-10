from fastapi import APIRouter
from controllers.groq_controller import get_trivia_question, print_statement, health_check

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/prova", response_model=dict)(print_statement)
router.get("/api/v1/get_trivia", response_model=dict)(get_trivia_question)