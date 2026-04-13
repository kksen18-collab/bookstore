"""Business logic for Order operations."""

from __future__ import annotations

import logging
from decimal import Decimal

from bookstore.db_models import BookORM, OrderItemORM, OrderORM, OrderStatus
from bookstore.exceptions import InvalidOrderStateError, NotFoundError, OutOfStockError
from bookstore.models.order import OrderCreate, OrderItemCreate, OrderUpdate
from bookstore.repositories.book import BookRepository
from bookstore.repositories.order import OrderRepository

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
    OrderStatus.SHIPPED: frozenset({OrderStatus.DELIVERED}),
    OrderStatus.DELIVERED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


def validate_status_transition(current: OrderStatus, target: OrderStatus) -> None:
    """Validate that a status transition is allowed.

    Args:
        current: The current order status.
        target: The desired new status.

    Raises:
        InvalidOrderStateError: If the transition is not allowed.
    """
    allowed = _VALID_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise InvalidOrderStateError(current.value, target.value)


class OrderService:
    """Business logic for Order operations."""

    def __init__(self, order_repository: OrderRepository, book_repository: BookRepository) -> None:
        self._order_repo = order_repository
        self._book_repo = book_repository

    async def get_order(self, order_id: int) -> OrderORM:
        """Retrieve an order by ID or raise NotFoundError."""
        order = await self._order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Order", order_id)
        return order

    async def list_orders(self, *, offset: int = 0, limit: int = 20) -> tuple[list[OrderORM], int]:
        """Retrieve a paginated list of orders."""
        return await self._order_repo.get_all(offset=offset, limit=limit)

    async def create_order(self, data: OrderCreate) -> OrderORM:
        """Create an order: validate stock, decrement quantities, calculate total.

        Args:
            data: The order creation request with items.

        Returns:
            The created order with items.

        Raises:
            NotFoundError: If a book in the order does not exist.
            OutOfStockError: If a book does not have sufficient stock.
        """
        items_with_books: list[tuple[OrderItemCreate, BookORM]] = []
        total = Decimal("0.00")

        for item in data.items:
            book = await self._book_repo.get_by_id(item.book_id)
            if book is None:
                raise NotFoundError("Book", item.book_id)
            if book.stock_quantity < item.quantity:
                raise OutOfStockError(item.book_id, item.quantity, book.stock_quantity)
            items_with_books.append((item, book))
            total += book.price * item.quantity

        for item, book in items_with_books:
            book.stock_quantity -= item.quantity

        order = OrderORM(
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            status=OrderStatus.PENDING,
            total_amount=total,
        )
        order_items = [
            OrderItemORM(
                book_id=item.book_id,
                quantity=item.quantity,
                unit_price=book.price,
            )
            for item, book in items_with_books
        ]
        order.items = order_items

        logger.info("Creating order for %s with %d items", data.customer_name, len(data.items))
        return await self._order_repo.create_with_items(order)

    async def update_order_status(self, order_id: int, data: OrderUpdate) -> OrderORM:
        """Update an order's status with valid transition check.

        Args:
            order_id: The order to update.
            data: The new status.

        Returns:
            The updated order.

        Raises:
            NotFoundError: If the order does not exist.
            InvalidOrderStateError: If the transition is not valid.
        """
        order = await self._order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Order", order_id)

        validate_status_transition(order.status, data.status)
        order.status = data.status
        logger.info("Order %d status changed to %s", order_id, data.status.value)
        return await self._order_repo.flush_and_refresh(order)
