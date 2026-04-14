from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.omdb_routes import router as omdb_router

app = create_app(
    title="OMDB Adapter",
    cors_origins=get_cors_origins()
)

app.include_router(health_router("OMDB Adapter", path="/"))
app.include_router(omdb_router)


