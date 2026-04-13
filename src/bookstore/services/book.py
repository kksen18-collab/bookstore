"""Business logic for Book operations."""

from __future__ import annotations

import logging

from bookstore.db_models import BookORM
from bookstore.exceptions import DuplicateISBNError, NotFoundError
from bookstore.models.book import BookCreate, BookUpdate
from bookstore.repositories.author import AuthorRepository
from bookstore.repositories.book import BookRepository

logger = logging.getLogger(__name__)


class BookService:
    """Business logic for Book operations."""

    def __init__(self, book_repository: BookRepository, author_repository: AuthorRepository) -> None:
        self._book_repo = book_repository
        self._author_repo = author_repository

    async def get_book(self, book_id: int) -> BookORM:
        """Retrieve a book by ID or raise NotFoundError."""
        book = await self._book_repo.get_by_id(book_id)
        if book is None:
            raise NotFoundError("Book", book_id)
        return book

    async def list_books(self, *, offset: int = 0, limit: int = 20) -> tuple[list[BookORM], int]:
        """Retrieve a paginated list of books."""
        return await self._book_repo.get_all(offset=offset, limit=limit)

    async def create_book(self, data: BookCreate) -> BookORM:
        """Create a new book after validating author and ISBN uniqueness."""
        author = await self._author_repo.get_by_id(data.author_id)
        if author is None:
            raise NotFoundError("Author", data.author_id)

        existing = await self._book_repo.get_by_isbn(data.isbn)
        if existing is not None:
            raise DuplicateISBNError(data.isbn)

        logger.info("Creating book: %s (ISBN: %s)", data.title, data.isbn)
        return await self._book_repo.create(data)

    async def update_book(self, book_id: int, data: BookUpdate) -> BookORM:
        """Update a book or raise NotFoundError."""
        if data.author_id is not None:
            author = await self._author_repo.get_by_id(data.author_id)
            if author is None:
                raise NotFoundError("Author", data.author_id)

        if data.isbn is not None:
            existing = await self._book_repo.get_by_isbn(data.isbn)
            if existing is not None and existing.id != book_id:
                raise DuplicateISBNError(data.isbn)

        book = await self._book_repo.update(book_id, data)
        if book is None:
            raise NotFoundError("Book", book_id)
        logger.info("Updated book %d", book_id)
        return book

    async def delete_book(self, book_id: int) -> None:
        """Delete a book or raise NotFoundError."""
        deleted = await self._book_repo.delete(book_id)
        if not deleted:
            raise NotFoundError("Book", book_id)
        logger.info("Deleted book %d", book_id)
