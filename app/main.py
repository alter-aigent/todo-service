from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.service_name, description="Todo service API", version="1.0.0")
    app.include_router(router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    async def _create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app


app = create_app()
