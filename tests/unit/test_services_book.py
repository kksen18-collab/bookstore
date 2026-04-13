"""Unit tests for BookService with mocked repositories."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from bookstore.exceptions import DuplicateISBNError, NotFoundError
from bookstore.models.book import BookCreate, BookUpdate
from bookstore.services.book import BookService


@pytest.fixture
def mock_book_repo() -> AsyncMock:
    """Provide a mocked BookRepository."""
    return AsyncMock()


@pytest.fixture
def mock_author_repo() -> AsyncMock:
    """Provide a mocked AuthorRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_book_repo: AsyncMock, mock_author_repo: AsyncMock) -> BookService:
    """Provide a BookService with mocked repositories."""
    return BookService(mock_book_repo, mock_author_repo)


class TestGetBook:
    """Tests for BookService.get_book."""

    async def test_returns_book_when_found(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        mock_book = MagicMock()
        mock_book.title = "Test Book"
        mock_book_repo.get_by_id.return_value = mock_book

        result = await service.get_book(1)
        assert result.title == "Test Book"

    async def test_raises_not_found(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_book(999)


class TestCreateBook:
    """Tests for BookService.create_book."""

    async def test_creates_book(
        self, service: BookService, mock_book_repo: AsyncMock, mock_author_repo: AsyncMock
    ) -> None:
        data = BookCreate(title="Test", isbn="9781234567890", price=Decimal("19.99"), author_id=1)
        mock_author_repo.get_by_id.return_value = MagicMock()
        mock_book_repo.get_by_isbn.return_value = None
        mock_book_repo.create.return_value = MagicMock()

        await service.create_book(data)
        mock_book_repo.create.assert_called_once_with(data)

    async def test_raises_not_found_when_author_missing(
        self, service: BookService, mock_author_repo: AsyncMock
    ) -> None:
        data = BookCreate(title="Test", isbn="9781234567890", price=Decimal("19.99"), author_id=999)
        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await service.create_book(data)
        assert exc_info.value.entity == "Author"

    async def test_raises_duplicate_isbn(
        self, service: BookService, mock_book_repo: AsyncMock, mock_author_repo: AsyncMock
    ) -> None:
        data = BookCreate(title="Test", isbn="9781234567890", price=Decimal("19.99"), author_id=1)
        mock_author_repo.get_by_id.return_value = MagicMock()
        mock_book_repo.get_by_isbn.return_value = MagicMock()

        with pytest.raises(DuplicateISBNError):
            await service.create_book(data)


class TestUpdateBook:
    """Tests for BookService.update_book."""

    async def test_updates_book(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        data = BookUpdate(title="Updated")
        mock_book_repo.update.return_value = MagicMock()

        await service.update_book(1, data)
        mock_book_repo.update.assert_called_once_with(1, data)

    async def test_raises_not_found(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        data = BookUpdate(title="Updated")
        mock_book_repo.update.return_value = None

        with pytest.raises(NotFoundError):
            await service.update_book(999, data)

    async def test_validates_author_on_update(self, service: BookService, mock_author_repo: AsyncMock) -> None:
        data = BookUpdate(author_id=999)
        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.update_book(1, data)

    async def test_validates_isbn_uniqueness_on_update(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        data = BookUpdate(isbn="9781234567890")
        existing = MagicMock()
        existing.id = 2
        mock_book_repo.get_by_isbn.return_value = existing

        with pytest.raises(DuplicateISBNError):
            await service.update_book(1, data)

    async def test_allows_same_isbn_on_same_book(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        data = BookUpdate(isbn="9781234567890")
        existing = MagicMock()
        existing.id = 1
        mock_book_repo.get_by_isbn.return_value = existing
        mock_book_repo.update.return_value = MagicMock()

        await service.update_book(1, data)
        mock_book_repo.update.assert_called_once()


class TestDeleteBook:
    """Tests for BookService.delete_book."""

    async def test_deletes_book(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        mock_book_repo.delete.return_value = True
        await service.delete_book(1)

    async def test_raises_not_found(self, service: BookService, mock_book_repo: AsyncMock) -> None:
        mock_book_repo.delete.return_value = False
        with pytest.raises(NotFoundError):
            await service.delete_book(999)
