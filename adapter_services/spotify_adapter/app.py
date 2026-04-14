from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.spotify_routes import router as spotify_router


app = create_app(
    title="Spotify Adapter",
    cors_origins=get_cors_origins(),
)

app.include_router(health_router("Spotify Adapter", path="/"))
app.include_router(spotify_router)