from fastapi import APIRouter
from controllers.spotify_controller import get_song, health_check, get_playlist, get_playlist_info

router = APIRouter()

router.get("/", response_model=dict)(health_check)
router.get("/api/v1/search_song", response_model=dict)(get_song)
#router.get("/api/v1/search_playlist", response_model=dict)(get_playlist)
router.get("/api/v1/search_playlist", response_model=dict)(get_playlist_info)