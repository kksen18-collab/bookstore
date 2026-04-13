"""Generic pagination response model."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper for list endpoints."""

    items: tuple[T, ...]
    total: int
    offset: int
    limit: int
