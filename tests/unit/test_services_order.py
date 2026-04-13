"""Unit tests for OrderService with mocked repositories."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from bookstore.db_models import OrderStatus
from bookstore.exceptions import InvalidOrderStateError, NotFoundError, OutOfStockError
from bookstore.models.order import OrderCreate, OrderItemCreate, OrderUpdate
from bookstore.services.order import OrderService, validate_status_transition


@pytest.fixture
def mock_order_repo() -> AsyncMock:
    """Provide a mocked OrderRepository."""
    return AsyncMock()


@pytest.fixture
def mock_book_repo() -> AsyncMock:
    """Provide a mocked BookRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_order_repo: AsyncMock, mock_book_repo: AsyncMock) -> OrderService:
    """Provide an OrderService with mocked repositories."""
    return OrderService(mock_order_repo, mock_book_repo)


def _make_book(book_id: int = 1, price: Decimal = Decimal("10.00"), stock: int = 10) -> MagicMock:
    """Create a mock book with given attributes."""
    book = MagicMock()
    book.id = book_id
    book.price = price
    book.stock_quantity = stock
    return book


class TestValidateStatusTransition:
    """Tests for the status transition validator."""

    def test_pending_to_confirmed(self) -> None:
        validate_status_transition(OrderStatus.PENDING, OrderStatus.CONFIRMED)

    def test_pending_to_cancelled(self) -> None:
        validate_status_transition(OrderStatus.PENDING, OrderStatus.CANCELLED)

    def test_confirmed_to_shipped(self) -> None:
        validate_status_transition(OrderStatus.CONFIRMED, OrderStatus.SHIPPED)

    def test_confirmed_to_cancelled(self) -> None:
        validate_status_transition(OrderStatus.CONFIRMED, OrderStatus.CANCELLED)

    def test_shipped_to_delivered(self) -> None:
        validate_status_transition(OrderStatus.SHIPPED, OrderStatus.DELIVERED)

    def test_pending_to_delivered_invalid(self) -> None:
        with pytest.raises(InvalidOrderStateError):
            validate_status_transition(OrderStatus.PENDING, OrderStatus.DELIVERED)

    def test_pending_to_shipped_invalid(self) -> None:
        with pytest.raises(InvalidOrderStateError):
            validate_status_transition(OrderStatus.PENDING, OrderStatus.SHIPPED)

    def test_cancelled_is_terminal(self) -> None:
        with pytest.raises(InvalidOrderStateError):
            validate_status_transition(OrderStatus.CANCELLED, OrderStatus.PENDING)

    def test_delivered_is_terminal(self) -> None:
        with pytest.raises(InvalidOrderStateError):
            validate_status_transition(OrderStatus.DELIVERED, OrderStatus.SHIPPED)


class TestCreateOrder:
    """Tests for OrderService.create_order."""

    async def test_creates_order(
        self, service: OrderService, mock_order_repo: AsyncMock, mock_book_repo: AsyncMock
    ) -> None:
        book = _make_book(book_id=1, price=Decimal("10.00"), stock=5)
        mock_book_repo.get_by_id.return_value = book
        mock_order_repo.create_with_items.return_value = MagicMock()

        data = OrderCreate(
            customer_name="John",
            customer_email="john@example.com",
            items=(OrderItemCreate(book_id=1, quantity=2),),
        )
        await service.create_order(data)

        mock_order_repo.create_with_items.assert_called_once()
        assert book.stock_quantity == 3

    async def test_raises_not_found_when_book_missing(self, service: OrderService, mock_book_repo: AsyncMock) -> None:
        mock_book_repo.get_by_id.return_value = None

        data = OrderCreate(
            customer_name="John",
            customer_email="john@example.com",
            items=(OrderItemCreate(book_id=999, quantity=1),),
        )
        with pytest.raises(NotFoundError):
            await service.create_order(data)

    async def test_raises_out_of_stock(self, service: OrderService, mock_book_repo: AsyncMock) -> None:
        book = _make_book(stock=1)
        mock_book_repo.get_by_id.return_value = book

        data = OrderCreate(
            customer_name="John",
            customer_email="john@example.com",
            items=(OrderItemCreate(book_id=1, quantity=5),),
        )
        with pytest.raises(OutOfStockError):
            await service.create_order(data)

    async def test_calculates_total(
        self, service: OrderService, mock_order_repo: AsyncMock, mock_book_repo: AsyncMock
    ) -> None:
        book = _make_book(price=Decimal("15.00"), stock=10)
        mock_book_repo.get_by_id.return_value = book
        mock_order_repo.create_with_items.side_effect = lambda order: order

        data = OrderCreate(
            customer_name="John",
            customer_email="john@example.com",
            items=(OrderItemCreate(book_id=1, quantity=3),),
        )
        result = await service.create_order(data)

        assert result.total_amount == Decimal("45.00")

    async def test_does_not_decrement_stock_on_validation_failure(
        self, service: OrderService, mock_book_repo: AsyncMock
    ) -> None:
        book1 = _make_book(book_id=1, stock=5)
        book2 = _make_book(book_id=2, stock=0)

        async def get_book(entity_id: int) -> MagicMock | None:
            if entity_id == 1:
                return book1
            return book2

        mock_book_repo.get_by_id.side_effect = get_book

        data = OrderCreate(
            customer_name="John",
            customer_email="john@example.com",
            items=(
                OrderItemCreate(book_id=1, quantity=1),
                OrderItemCreate(book_id=2, quantity=1),
            ),
        )
        with pytest.raises(OutOfStockError):
            await service.create_order(data)

        assert book1.stock_quantity == 5


class TestUpdateOrderStatus:
    """Tests for OrderService.update_order_status."""

    async def test_updates_status(self, service: OrderService, mock_order_repo: AsyncMock) -> None:
        mock_order = MagicMock()
        mock_order.status = OrderStatus.PENDING
        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.flush_and_refresh.return_value = mock_order

        data = OrderUpdate(status=OrderStatus.CONFIRMED)
        await service.update_order_status(1, data)

        assert mock_order.status == OrderStatus.CONFIRMED

    async def test_raises_not_found(self, service: OrderService, mock_order_repo: AsyncMock) -> None:
        mock_order_repo.get_by_id.return_value = None
        data = OrderUpdate(status=OrderStatus.CONFIRMED)

        with pytest.raises(NotFoundError):
            await service.update_order_status(999, data)

    async def test_raises_invalid_transition(self, service: OrderService, mock_order_repo: AsyncMock) -> None:
        mock_order = MagicMock()
        mock_order.status = OrderStatus.DELIVERED
        mock_order_repo.get_by_id.return_value = mock_order

        data = OrderUpdate(status=OrderStatus.SHIPPED)

        with pytest.raises(InvalidOrderStateError):
            await service.update_order_status(1, data)
