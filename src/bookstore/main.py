"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bookstore.config import get_settings
from bookstore.dependencies import init_database
from bookstore.routes.authors import router as authors_router
from bookstore.routes.books import router as books_router
from bookstore.routes.error_handlers import register_error_handlers
from bookstore.routes.orders import router as orders_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: initialize and tear down resources."""
    settings = get_settings()
    database = init_database(settings)
    await database.create_tables()
    logger.info("Database tables created")
    yield
    await database.close()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(authors_router, prefix="/api/v1")
    app.include_router(books_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    register_error_handlers(app)
    return app


app = create_app()
