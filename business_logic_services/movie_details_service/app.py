from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.movie_details_routes import router as movie_details_router

app = create_app(
    title="Movie Details Service",
    cors_origins=get_cors_origins()
)

app.include_router(health_router("Movie Details Service", path="/"))
app.include_router(movie_details_router)