"""Repository for Author data access."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.db_models import AuthorORM
from bookstore.models.author import AuthorCreate, AuthorUpdate
from bookstore.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorORM]):
    """SQLAlchemy implementation of Author data access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: int) -> AuthorORM | None:
        """Retrieve an author by ID."""
        stmt = select(AuthorORM).where(AuthorORM.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, offset: int = 0, limit: int = 20) -> tuple[list[AuthorORM], int]:
        """Retrieve a paginated list of authors and total count."""
        count_stmt = select(func.count()).select_from(AuthorORM)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = select(AuthorORM).offset(offset).limit(limit).order_by(AuthorORM.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, data: AuthorCreate) -> AuthorORM:
        """Create a new author."""
        author = AuthorORM(**data.model_dump())
        self._session.add(author)
        await self._session.flush()
        await self._session.refresh(author)
        return author

    async def update(self, entity_id: int, data: AuthorUpdate) -> AuthorORM | None:
        """Update an author. Returns None if not found."""
        author = await self.get_by_id(entity_id)
        if author is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(author, field, value)
        await self._session.flush()
        await self._session.refresh(author)
        return author

    async def delete(self, entity_id: int) -> bool:
        """Delete an author. Returns True if deleted."""
        author = await self.get_by_id(entity_id)
        if author is None:
            return False
        await self._session.delete(author)
        await self._session.flush()
        return True
