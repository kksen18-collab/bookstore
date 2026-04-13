"""Pydantic schemas for Book API boundary."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from bookstore.models.author import AuthorResponse


class BookCreate(BaseModel):
    """Schema for creating a book."""

    title: str = Field(min_length=1, max_length=500)
    isbn: str = Field(min_length=10, max_length=13)
    price: Decimal = Field(gt=Decimal("0"), decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    author_id: int


class BookUpdate(BaseModel):
    """Schema for partially updating a book."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    isbn: str | None = Field(default=None, min_length=10, max_length=13)
    price: Decimal | None = Field(default=None, gt=Decimal("0"), decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    author_id: int | None = None


class BookResponse(BaseModel):
    """Schema for book API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str
    price: Decimal
    stock_quantity: int
    author_id: int
    author: AuthorResponse
    created_at: datetime.datetime
