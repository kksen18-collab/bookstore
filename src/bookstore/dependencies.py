"""FastAPI dependency injection wiring."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.config import Settings
from bookstore.database import Database
from bookstore.repositories.author import AuthorRepository
from bookstore.repositories.book import BookRepository
from bookstore.repositories.order import OrderRepository
from bookstore.services.author import AuthorService
from bookstore.services.book import BookService
from bookstore.services.order import OrderService

_database: Database | None = None


def get_database() -> Database:
    """Return the global Database instance."""
    if _database is None:
        msg = "Database not initialized. Call init_database() first."
        raise RuntimeError(msg)
    return _database


def init_database(settings: Settings) -> Database:
    """Initialize the global Database instance."""
    global _database
    _database = Database(settings)
    return _database


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Yield a transactional async session for a single request."""
    db = get_database()
    async for session in db.get_session():
        async with session.begin():
            yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_author_repository(session: SessionDep) -> AuthorRepository:
    """Provide an AuthorRepository bound to the request session."""
    return AuthorRepository(session)


def get_book_repository(session: SessionDep) -> BookRepository:
    """Provide a BookRepository bound to the request session."""
    return BookRepository(session)


def get_order_repository(session: SessionDep) -> OrderRepository:
    """Provide an OrderRepository bound to the request session."""
    return OrderRepository(session)


AuthorRepoDep = Annotated[AuthorRepository, Depends(get_author_repository)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
OrderRepoDep = Annotated[OrderRepository, Depends(get_order_repository)]


def get_author_service(repo: AuthorRepoDep) -> AuthorService:
    """Provide an AuthorService with injected repository."""
    return AuthorService(repo)


def get_book_service(book_repo: BookRepoDep, author_repo: AuthorRepoDep) -> BookService:
    """Provide a BookService with injected repositories."""
    return BookService(book_repo, author_repo)


def get_order_service(order_repo: OrderRepoDep, book_repo: BookRepoDep) -> OrderService:
    """Provide an OrderService with injected repositories."""
    return OrderService(order_repo, book_repo)


AuthorServiceDep = Annotated[AuthorService, Depends(get_author_service)]
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
