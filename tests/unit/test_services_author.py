"""Unit tests for AuthorService with mocked repository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bookstore.exceptions import NotFoundError
from bookstore.models.author import AuthorCreate, AuthorUpdate
from bookstore.services.author import AuthorService


@pytest.fixture
def mock_repo() -> AsyncMock:
    """Provide a mocked AuthorRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> AuthorService:
    """Provide an AuthorService with mocked repository."""
    return AuthorService(mock_repo)


class TestGetAuthor:
    """Tests for AuthorService.get_author."""

    async def test_returns_author_when_found(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_author = MagicMock()
        mock_author.id = 1
        mock_author.name = "Jane Doe"
        mock_repo.get_by_id.return_value = mock_author

        result = await service.get_author(1)

        assert result.name == "Jane Doe"
        mock_repo.get_by_id.assert_called_once_with(1)

    async def test_raises_not_found_when_missing(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await service.get_author(999)

        assert exc_info.value.entity == "Author"
        assert exc_info.value.entity_id == 999


class TestListAuthors:
    """Tests for AuthorService.list_authors."""

    async def test_delegates_to_repository(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_repo.get_all.return_value = ([], 0)

        result = await service.list_authors(offset=5, limit=10)

        assert result == ([], 0)
        mock_repo.get_all.assert_called_once_with(offset=5, limit=10)


class TestCreateAuthor:
    """Tests for AuthorService.create_author."""

    async def test_creates_author(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        data = AuthorCreate(name="Test Author", bio="A bio")
        mock_author = MagicMock()
        mock_author.name = "Test Author"
        mock_repo.create.return_value = mock_author

        result = await service.create_author(data)

        assert result.name == "Test Author"
        mock_repo.create.assert_called_once_with(data)


class TestUpdateAuthor:
    """Tests for AuthorService.update_author."""

    async def test_updates_author(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        data = AuthorUpdate(name="Updated")
        mock_author = MagicMock()
        mock_author.name = "Updated"
        mock_repo.update.return_value = mock_author

        result = await service.update_author(1, data)

        assert result.name == "Updated"
        mock_repo.update.assert_called_once_with(1, data)

    async def test_raises_not_found(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_repo.update.return_value = None
        data = AuthorUpdate(name="Updated")

        with pytest.raises(NotFoundError):
            await service.update_author(999, data)


class TestDeleteAuthor:
    """Tests for AuthorService.delete_author."""

    async def test_deletes_author(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_repo.delete.return_value = True
        await service.delete_author(1)
        mock_repo.delete.assert_called_once_with(1)

    async def test_raises_not_found(self, service: AuthorService, mock_repo: AsyncMock) -> None:
        mock_repo.delete.return_value = False

        with pytest.raises(NotFoundError):
            await service.delete_author(999)
