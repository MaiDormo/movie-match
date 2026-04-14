from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.tmdb_routes import router as tmdb_router

app = create_app(
    title="TMDB Adapter",
    cors_origins=get_cors_origins()
)

app.include_router(health_router("TMDB Adapter", path="/"))
app.include_router(tmdb_router)