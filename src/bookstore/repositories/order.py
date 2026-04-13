"""Repository for Order data access."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.db_models import OrderORM
from bookstore.models.order import OrderCreate
from bookstore.repositories.base import BaseRepository


class OrderRepository(BaseRepository[OrderORM, OrderCreate, OrderCreate]):
    """SQLAlchemy implementation of Order data access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: int) -> OrderORM | None:
        """Retrieve an order by ID with items eagerly loaded."""
        stmt = select(OrderORM).where(OrderORM.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, offset: int = 0, limit: int = 20) -> tuple[list[OrderORM], int]:
        """Retrieve a paginated list of orders and total count."""
        count_stmt = select(func.count()).select_from(OrderORM)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = select(OrderORM).offset(offset).limit(limit).order_by(OrderORM.id.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def create(self, data: OrderCreate) -> OrderORM:
        """Not used directly — use create_with_items instead."""
        raise NotImplementedError("Use create_with_items for order creation")

    async def create_with_items(self, order: OrderORM) -> OrderORM:
        """Persist a fully-composed order with its items."""
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def update(self, entity_id: int, data: OrderCreate) -> OrderORM | None:
        """Not used directly — use update_status via the service layer."""
        raise NotImplementedError("Use the service layer for order updates")

    async def flush_and_refresh(self, order: OrderORM) -> OrderORM:
        """Flush pending changes and refresh the order from the database."""
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def delete(self, entity_id: int) -> bool:
        """Orders cannot be deleted, only cancelled."""
        raise NotImplementedError("Orders cannot be deleted, only cancelled")
