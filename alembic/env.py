from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.db.base import Base

# Alembic Config object provides access to values within the .ini file.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models so Base.metadata is populated.
# If you add new models, make sure they are imported somewhere under app/models.
from app import models  # noqa: F401  # isort: skip

target_metadata = Base.metadata


def get_database_url() -> str:
    # Prefer env var (works for local and Docker). Fallback is empty, alembic will error clearly.
    return os.environ.get("DATABASE_URL", "")


def run_migrations_offline() -> None:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run_migrations()


