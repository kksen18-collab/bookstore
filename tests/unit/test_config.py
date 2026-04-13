"""Tests for application configuration."""

from __future__ import annotations

from bookstore.config import Settings, get_settings


class TestSettings:
    """Tests for the Settings class."""

    def test_defaults(self) -> None:
        settings = Settings()
        assert settings.database_url == "sqlite+aiosqlite:///./bookstore.db"
        assert settings.debug is False
        assert settings.app_title == "Bookstore API"
        assert settings.app_version == "0.1.0"

    def test_custom_values(self) -> None:
        settings = Settings(database_url="sqlite+aiosqlite://", debug=True)
        assert settings.database_url == "sqlite+aiosqlite://"
        assert settings.debug is True


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_returns_settings(self) -> None:
        settings = get_settings()
        assert isinstance(settings, Settings)
