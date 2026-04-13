"""Shared test fixtures for the bookstore test suite."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bookstore.db_models import Base
from bookstore.dependencies import get_session
from bookstore.main import create_app


@pytest.fixture
async def async_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession]:
    """Provide a transactional session that rolls back after each test."""
    session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with session_factory() as session, session.begin():
        yield session
        await session.rollback()


@pytest.fixture
async def client(async_engine) -> AsyncGenerator[AsyncClient]:
    """Provide an async HTTP test client with database overrides."""
    app = create_app()
    session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    async def override_session() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session, session.begin():
            yield session

    app.dependency_overrides[get_session] = override_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
