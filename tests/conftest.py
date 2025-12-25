import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    # Ensure we don't accidentally point at a real DB.
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    os.environ.setdefault("ENV", "test")


@pytest.fixture
async def client():
    # Import app after env vars are set
    from app.main import app as fastapi_app
    from app.core.database import Base

    # Ensure model metadata is registered on the Base before create_all()
    import app.models  # noqa: F401

    # Mock DB for tests: single in-memory SQLite connection shared across sessions/requests.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.api import deps as deps_module

    async def override_get_db_session():
        async with async_session() as session:
            yield session

    fastapi_app.dependency_overrides[deps_module.get_db_session] = override_get_db_session

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
    await engine.dispose()
