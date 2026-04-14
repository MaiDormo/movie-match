from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.youtube_routes import router as youtube_router

app = create_app(
    title="YouTube Adapter",
    cors_origins=get_cors_origins(),
)

app.include_router(health_router("YouTube Adapter", path="/"))
app.include_router(youtube_router)