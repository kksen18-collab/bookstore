"""Repository for Book data access."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.db_models import BookORM
from bookstore.models.book import BookCreate, BookUpdate
from bookstore.repositories.base import BaseRepository


class BookRepository(BaseRepository[BookORM]):
    """SQLAlchemy implementation of Book data access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: int) -> BookORM | None:
        """Retrieve a book by ID."""
        stmt = select(BookORM).where(BookORM.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_isbn(self, isbn: str) -> BookORM | None:
        """Retrieve a book by ISBN."""
        stmt = select(BookORM).where(BookORM.isbn == isbn)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, offset: int = 0, limit: int = 20) -> tuple[list[BookORM], int]:
        """Retrieve a paginated list of books and total count."""
        count_stmt = select(func.count()).select_from(BookORM)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = select(BookORM).offset(offset).limit(limit).order_by(BookORM.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, data: BookCreate) -> BookORM:
        """Create a new book."""
        book = BookORM(**data.model_dump())
        self._session.add(book)
        await self._session.flush()
        await self._session.refresh(book)
        return book

    async def update(self, entity_id: int, data: BookUpdate) -> BookORM | None:
        """Update a book. Returns None if not found."""
        book = await self.get_by_id(entity_id)
        if book is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(book, field, value)
        await self._session.flush()
        await self._session.refresh(book)
        return book

    async def delete(self, entity_id: int) -> bool:
        """Delete a book. Returns True if deleted."""
        book = await self.get_by_id(entity_id)
        if book is None:
            return False
        await self._session.delete(book)
        await self._session.flush()
        return True
