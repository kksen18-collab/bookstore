"""Pydantic schemas for Author API boundary."""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorCreate(BaseModel):
    """Schema for creating an author."""

    name: str = Field(min_length=1, max_length=255)
    bio: str | None = None


class AuthorUpdate(BaseModel):
    """Schema for partially updating an author."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    bio: str | None = None


class AuthorResponse(BaseModel):
    """Schema for author API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None
    created_at: datetime.datetime
