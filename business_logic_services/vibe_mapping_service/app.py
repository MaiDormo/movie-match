from shared.common.app_factory import create_app
from shared.common.health import health_router
from shared.common.config import get_cors_origins
from routes.vibe_routes import router as vibe_router

app = create_app(
        title="Vibe Service",
        cors_origins=get_cors_origins()
)

app.include_router(health_router("Vibe Service", path="/"))
app.include_router(vibe_router)
