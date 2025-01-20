from fastapi import APIRouter
from controllers.genre_db_controller import create_genre, list_genres, get_genre, update_genre, delete_genre, health_check 


router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.post("/api/v1/genre", response_model=dict)(create_genre)
router.get("/api/v1/genres", response_model=dict)(list_genres)
router.get("/api/v1/genre", response_model=dict)(get_genre)
router.put("/api/v1/genre", response_model=dict)(update_genre)
router.delete("/api/v1/genre")(delete_genre)