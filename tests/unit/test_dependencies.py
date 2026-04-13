"""Tests for the dependency injection module."""

from __future__ import annotations

import pytest

import bookstore.dependencies as deps
from bookstore.config import Settings


class TestDependencies:
    """Tests for dependency initialization and access."""

    def test_get_database_raises_when_not_initialized(self) -> None:
        original = deps._database
        deps._database = None
        try:
            with pytest.raises(RuntimeError, match="Database not initialized"):
                deps.get_database()
        finally:
            deps._database = original

    def test_init_database(self) -> None:
        original = deps._database
        try:
            settings = Settings(database_url="sqlite+aiosqlite://")
            db = deps.init_database(settings)
            assert db is not None
            assert deps.get_database() is db
        finally:
            deps._database = original
