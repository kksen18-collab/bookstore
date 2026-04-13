"""Abstract base repository defining the common data access contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)


class BaseRepository(ABC, Generic[T, CreateT, UpdateT]):
    """Abstract base for all repositories."""

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> T | None:
        """Retrieve an entity by its primary key."""

    @abstractmethod
    async def get_all(self, *, offset: int = 0, limit: int = 20) -> tuple[list[T], int]:
        """Retrieve a paginated list of entities and the total count."""

    @abstractmethod
    async def create(self, data: CreateT) -> T:
        """Create a new entity from the given data."""

    @abstractmethod
    async def update(self, entity_id: int, data: UpdateT) -> T | None:
        """Update an entity. Returns None if not found."""

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete an entity. Returns True if deleted, False if not found."""
