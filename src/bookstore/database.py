"""Async SQLAlchemy engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from bookstore.config import Settings


class Database:
    """Manages the async SQLAlchemy engine and session factory."""

    def __init__(self, settings: Settings) -> None:
        self._engine: AsyncEngine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Return the async engine."""
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the session factory."""
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """Yield a transactional async session."""
        async with self._session_factory() as session:
            yield session

    async def create_tables(self) -> None:
        """Create all database tables from ORM metadata."""
        from bookstore.db_models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Dispose of the engine and release connections."""
        await self._engine.dispose()
