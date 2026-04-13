"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKSTORE_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str = "sqlite+aiosqlite:///./bookstore.db"
    debug: bool = False
    app_title: str = "Bookstore API"
    app_version: str = "0.1.0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
