from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _ensure_sqlite_directory(database_url: str) -> None:
    sqlite_prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return

    raw_path = database_url.removeprefix(sqlite_prefix)
    if raw_path.startswith("./"):
        raw_path = raw_path[2:]

    db_path = Path(raw_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)


def init_engine() -> None:
    global _engine, _session_factory
    if _engine is not None and _session_factory is not None:
        return

    settings = get_settings()
    _ensure_sqlite_directory(settings.sqlite_url)

    _engine = create_async_engine(settings.sqlite_url, echo=settings.debug, future=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    from app.models.weather import WeatherRecord

    _ = WeatherRecord
    init_engine()
    if _engine is None:
        raise RuntimeError("Database engine is not initialized")

    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_session() -> AsyncIterator[AsyncSession]:
    if _session_factory is None:
        init_engine()
    if _session_factory is None:
        raise RuntimeError("Database session factory is not initialized")

    async with _session_factory() as session:
        yield session


async def check_database_health() -> tuple[str, str | None]:
    init_engine()
    if _engine is None:
        return "error", "Database engine is not initialized"

    try:
        async with _engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1")
    except Exception as exc:
        return "error", str(exc)
    return "ok", None
