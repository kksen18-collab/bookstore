"""Tests for the Database class."""

from __future__ import annotations

from bookstore.config import Settings
from bookstore.database import Database


class TestDatabase:
    """Tests for the Database lifecycle."""

    async def test_create_and_close(self) -> None:
        settings = Settings(database_url="sqlite+aiosqlite://")
        db = Database(settings)
        assert db.engine is not None
        assert db.session_factory is not None
        await db.create_tables()
        await db.close()

    async def test_get_session_yields_session(self) -> None:
        settings = Settings(database_url="sqlite+aiosqlite://")
        db = Database(settings)
        await db.create_tables()

        async for session in db.get_session():
            assert session is not None
            break

        await db.close()
