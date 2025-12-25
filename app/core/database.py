import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


_engine_kwargs: dict = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite+aiosqlite:///:memory:"):
    # Ensure all sessions share the same in-memory DB connection during tests.
    _engine_kwargs.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    )

engine = create_async_engine(settings.database_url, **_engine_kwargs)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

_db_initialized = False
_db_init_lock = asyncio.Lock()


async def init_db() -> None:
    """Create tables (idempotent).

    Tests use ASGITransport without lifespan, so we can't rely on FastAPI
    startup events to run. This ensures tables exist the first time a DB
    session is requested.
    """

    global _db_initialized
    if _db_initialized:
        return
    async with _db_init_lock:
        if _db_initialized:
            return
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _db_initialized = True


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    await init_db()
    async with async_session_maker() as session:
        yield session
