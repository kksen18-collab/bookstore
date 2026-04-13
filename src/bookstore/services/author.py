"""Business logic for Author operations."""

from __future__ import annotations

import logging

from bookstore.db_models import AuthorORM
from bookstore.exceptions import NotFoundError
from bookstore.models.author import AuthorCreate, AuthorUpdate
from bookstore.repositories.author import AuthorRepository

logger = logging.getLogger(__name__)


class AuthorService:
    """Business logic for Author operations."""

    def __init__(self, repository: AuthorRepository) -> None:
        self._repository = repository

    async def get_author(self, author_id: int) -> AuthorORM:
        """Retrieve an author by ID or raise NotFoundError."""
        author = await self._repository.get_by_id(author_id)
        if author is None:
            raise NotFoundError("Author", author_id)
        return author

    async def list_authors(self, *, offset: int = 0, limit: int = 20) -> tuple[list[AuthorORM], int]:
        """Retrieve a paginated list of authors."""
        return await self._repository.get_all(offset=offset, limit=limit)

    async def create_author(self, data: AuthorCreate) -> AuthorORM:
        """Create a new author."""
        logger.info("Creating author: %s", data.name)
        return await self._repository.create(data)

    async def update_author(self, author_id: int, data: AuthorUpdate) -> AuthorORM:
        """Update an author or raise NotFoundError."""
        author = await self._repository.update(author_id, data)
        if author is None:
            raise NotFoundError("Author", author_id)
        logger.info("Updated author %d", author_id)
        return author

    async def delete_author(self, author_id: int) -> None:
        """Delete an author or raise NotFoundError."""
        deleted = await self._repository.delete(author_id)
        if not deleted:
            raise NotFoundError("Author", author_id)
        logger.info("Deleted author %d", author_id)
