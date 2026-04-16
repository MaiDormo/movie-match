from shared.common.app_factory import create_app
from shared.common.config import get_cors_origins
from shared.common.health import health_router

from routes.llm_routes import router as llm_router

app = create_app(
    title="LLM Adapter",
    cors_origins=get_cors_origins()
)

app.include_router(health_router("LLM Adapter", path="/"))
app.include_router(llm_router)
