"""Tests for Pydantic schema validation."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from bookstore.db_models import OrderStatus
from bookstore.models.author import AuthorCreate, AuthorUpdate
from bookstore.models.book import BookCreate, BookUpdate
from bookstore.models.order import OrderCreate, OrderItemCreate, OrderUpdate
from bookstore.models.pagination import PaginatedResponse


class TestAuthorCreate:
    """Tests for AuthorCreate schema."""

    def test_valid(self) -> None:
        author = AuthorCreate(name="Jane Doe", bio="A great author")
        assert author.name == "Jane Doe"
        assert author.bio == "A great author"

    def test_name_required(self) -> None:
        with pytest.raises(ValidationError):
            AuthorCreate(name="", bio="test")

    def test_bio_optional(self) -> None:
        author = AuthorCreate(name="Jane Doe")
        assert author.bio is None


class TestAuthorUpdate:
    """Tests for AuthorUpdate schema."""

    def test_partial_update(self) -> None:
        update = AuthorUpdate(name="New Name")
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"name": "New Name"}

    def test_all_fields_optional(self) -> None:
        update = AuthorUpdate()
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {}


class TestBookCreate:
    """Tests for BookCreate schema."""

    def test_valid(self) -> None:
        book = BookCreate(title="Test Book", isbn="9781234567890", price=Decimal("19.99"), author_id=1)
        assert book.title == "Test Book"
        assert book.stock_quantity == 0

    def test_rejects_negative_price(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="Test", isbn="9781234567890", price=Decimal("-1.00"), author_id=1)

    def test_rejects_zero_price(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="Test", isbn="9781234567890", price=Decimal("0.00"), author_id=1)

    def test_rejects_empty_title(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="", isbn="9781234567890", price=Decimal("19.99"), author_id=1)

    def test_rejects_short_isbn(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="Test", isbn="123", price=Decimal("19.99"), author_id=1)

    def test_stock_quantity_defaults_zero(self) -> None:
        book = BookCreate(title="Test", isbn="9781234567890", price=Decimal("9.99"), author_id=1)
        assert book.stock_quantity == 0

    def test_rejects_negative_stock(self) -> None:
        with pytest.raises(ValidationError):
            BookCreate(title="Test", isbn="9781234567890", price=Decimal("9.99"), stock_quantity=-1, author_id=1)


class TestBookUpdate:
    """Tests for BookUpdate schema."""

    def test_partial_update(self) -> None:
        update = BookUpdate(title="Updated Title")
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {"title": "Updated Title"}


class TestOrderItemCreate:
    """Tests for OrderItemCreate schema."""

    def test_valid(self) -> None:
        item = OrderItemCreate(book_id=1, quantity=2)
        assert item.book_id == 1
        assert item.quantity == 2

    def test_rejects_zero_quantity(self) -> None:
        with pytest.raises(ValidationError):
            OrderItemCreate(book_id=1, quantity=0)

    def test_rejects_negative_quantity(self) -> None:
        with pytest.raises(ValidationError):
            OrderItemCreate(book_id=1, quantity=-1)


class TestOrderCreate:
    """Tests for OrderCreate schema."""

    def test_valid(self) -> None:
        order = OrderCreate(
            customer_name="John Doe",
            customer_email="john@example.com",
            items=(OrderItemCreate(book_id=1, quantity=1),),
        )
        assert order.customer_name == "John Doe"
        assert len(order.items) == 1

    def test_rejects_empty_items(self) -> None:
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_name="John Doe",
                customer_email="john@example.com",
                items=(),
            )

    def test_rejects_invalid_email(self) -> None:
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_name="John Doe",
                customer_email="not-an-email",
                items=(OrderItemCreate(book_id=1, quantity=1),),
            )

    def test_rejects_empty_customer_name(self) -> None:
        with pytest.raises(ValidationError):
            OrderCreate(
                customer_name="",
                customer_email="john@example.com",
                items=(OrderItemCreate(book_id=1, quantity=1),),
            )


class TestOrderUpdate:
    """Tests for OrderUpdate schema."""

    def test_valid_status(self) -> None:
        update = OrderUpdate(status=OrderStatus.CONFIRMED)
        assert update.status == OrderStatus.CONFIRMED

    def test_rejects_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            OrderUpdate(status="invalid_status")


class TestPaginatedResponse:
    """Tests for PaginatedResponse schema."""

    def test_valid(self) -> None:
        response = PaginatedResponse[str](items=("a", "b"), total=10, offset=0, limit=20)
        assert response.items == ("a", "b")
        assert response.total == 10
