from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.service_name, description="Todo service API", version="1.0.0")
    app.include_router(router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
