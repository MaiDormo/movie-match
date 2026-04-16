from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router
from routes.streaming_availability_routes import router as stream_avail_router

app = create_app(
    title="Streaming Availability Adapter",
    cors_origins=get_cors_origins()
)

app.include_router(health_router("Streaming Availability Adapter", path="/"))
app.include_router(stream_avail_router)