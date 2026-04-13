"""Integration tests for repositories using a real database session."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.db_models import OrderItemORM, OrderORM, OrderStatus
from bookstore.models.author import AuthorCreate, AuthorUpdate
from bookstore.models.book import BookCreate, BookUpdate
from bookstore.repositories.author import AuthorRepository
from bookstore.repositories.book import BookRepository
from bookstore.repositories.order import OrderRepository


@pytest.mark.integration
class TestAuthorRepository:
    """Integration tests for AuthorRepository."""

    async def test_create_and_get(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        author = await repo.create(AuthorCreate(name="Jane Doe", bio="A bio"))
        assert author.id is not None
        assert author.name == "Jane Doe"

        fetched = await repo.get_by_id(author.id)
        assert fetched is not None
        assert fetched.name == "Jane Doe"

    async def test_get_by_id_not_found(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        result = await repo.get_by_id(9999)
        assert result is None

    async def test_get_all(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        await repo.create(AuthorCreate(name="Author 1"))
        await repo.create(AuthorCreate(name="Author 2"))
        await repo.create(AuthorCreate(name="Author 3"))

        authors, total = await repo.get_all(offset=0, limit=2)
        assert total == 3
        assert len(authors) == 2

    async def test_update(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        author = await repo.create(AuthorCreate(name="Old Name"))

        updated = await repo.update(author.id, AuthorUpdate(name="New Name"))
        assert updated is not None
        assert updated.name == "New Name"

    async def test_update_not_found(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        result = await repo.update(9999, AuthorUpdate(name="Test"))
        assert result is None

    async def test_delete(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        author = await repo.create(AuthorCreate(name="To Delete"))

        assert await repo.delete(author.id) is True
        assert await repo.get_by_id(author.id) is None

    async def test_delete_not_found(self, db_session: AsyncSession) -> None:
        repo = AuthorRepository(db_session)
        assert await repo.delete(9999) is False


@pytest.mark.integration
class TestBookRepository:
    """Integration tests for BookRepository."""

    async def test_create_and_get(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        repo = BookRepository(db_session)
        book = await repo.create(
            BookCreate(title="Test Book", isbn="9781234567890", price=Decimal("19.99"), author_id=author.id)
        )
        assert book.id is not None
        assert book.title == "Test Book"

        fetched = await repo.get_by_id(book.id)
        assert fetched is not None
        assert fetched.isbn == "9781234567890"

    async def test_get_by_isbn(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        repo = BookRepository(db_session)
        await repo.create(BookCreate(title="Book", isbn="9781234567890", price=Decimal("10.00"), author_id=author.id))

        found = await repo.get_by_isbn("9781234567890")
        assert found is not None
        assert found.title == "Book"

        not_found = await repo.get_by_isbn("0000000000000")
        assert not_found is None

    async def test_get_all(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        repo = BookRepository(db_session)
        await repo.create(BookCreate(title="Book 1", isbn="9781234567891", price=Decimal("10.00"), author_id=author.id))
        await repo.create(BookCreate(title="Book 2", isbn="9781234567892", price=Decimal("20.00"), author_id=author.id))

        books, total = await repo.get_all(offset=0, limit=10)
        assert total == 2
        assert len(books) == 2

    async def test_update(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        repo = BookRepository(db_session)
        book = await repo.create(
            BookCreate(title="Old Title", isbn="9781234567890", price=Decimal("10.00"), author_id=author.id)
        )

        updated = await repo.update(book.id, BookUpdate(title="New Title"))
        assert updated is not None
        assert updated.title == "New Title"

    async def test_update_not_found(self, db_session: AsyncSession) -> None:
        repo = BookRepository(db_session)
        result = await repo.update(9999, BookUpdate(title="Test"))
        assert result is None

    async def test_delete(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        repo = BookRepository(db_session)
        book = await repo.create(
            BookCreate(title="To Delete", isbn="9781234567890", price=Decimal("10.00"), author_id=author.id)
        )

        assert await repo.delete(book.id) is True
        assert await repo.get_by_id(book.id) is None

    async def test_delete_not_found(self, db_session: AsyncSession) -> None:
        repo = BookRepository(db_session)
        assert await repo.delete(9999) is False


@pytest.mark.integration
class TestOrderRepository:
    """Integration tests for OrderRepository."""

    async def test_create_with_items_and_get(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        book_repo = BookRepository(db_session)
        book = await book_repo.create(
            BookCreate(
                title="Book", isbn="9781234567890", price=Decimal("25.00"), stock_quantity=10, author_id=author.id
            )
        )

        repo = OrderRepository(db_session)
        order = OrderORM(
            customer_name="John",
            customer_email="john@example.com",
            status=OrderStatus.PENDING,
            total_amount=Decimal("50.00"),
        )
        order.items = [OrderItemORM(book_id=book.id, quantity=2, unit_price=Decimal("25.00"))]

        created = await repo.create_with_items(order)
        assert created.id is not None
        assert len(created.items) == 1

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.customer_name == "John"

    async def test_get_by_id_not_found(self, db_session: AsyncSession) -> None:
        repo = OrderRepository(db_session)
        result = await repo.get_by_id(9999)
        assert result is None

    async def test_get_all(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        book_repo = BookRepository(db_session)
        book = await book_repo.create(
            BookCreate(
                title="Book", isbn="9781234567890", price=Decimal("10.00"), stock_quantity=10, author_id=author.id
            )
        )

        repo = OrderRepository(db_session)
        for _ in range(3):
            order = OrderORM(
                customer_name="John",
                customer_email="john@example.com",
                status=OrderStatus.PENDING,
                total_amount=Decimal("10.00"),
            )
            order.items = [OrderItemORM(book_id=book.id, quantity=1, unit_price=Decimal("10.00"))]
            await repo.create_with_items(order)

        orders, total = await repo.get_all(offset=0, limit=2)
        assert total == 3
        assert len(orders) == 2

    async def test_flush_and_refresh(self, db_session: AsyncSession) -> None:
        author_repo = AuthorRepository(db_session)
        author = await author_repo.create(AuthorCreate(name="Author"))

        book_repo = BookRepository(db_session)
        book = await book_repo.create(
            BookCreate(
                title="Book", isbn="9781234567890", price=Decimal("25.00"), stock_quantity=10, author_id=author.id
            )
        )

        repo = OrderRepository(db_session)
        order = OrderORM(
            customer_name="John",
            customer_email="john@example.com",
            status=OrderStatus.PENDING,
            total_amount=Decimal("25.00"),
        )
        order.items = [OrderItemORM(book_id=book.id, quantity=1, unit_price=Decimal("25.00"))]
        created = await repo.create_with_items(order)

        created.status = OrderStatus.CONFIRMED
        refreshed = await repo.flush_and_refresh(created)
        assert refreshed.status == OrderStatus.CONFIRMED

    async def test_create_raises_not_implemented(self, db_session: AsyncSession) -> None:
        repo = OrderRepository(db_session)
        with pytest.raises(NotImplementedError):
            await repo.create(None)  # type: ignore[arg-type]

    async def test_update_raises_not_implemented(self, db_session: AsyncSession) -> None:
        repo = OrderRepository(db_session)
        with pytest.raises(NotImplementedError):
            await repo.update(1, None)  # type: ignore[arg-type]

    async def test_delete_raises_not_implemented(self, db_session: AsyncSession) -> None:
        repo = OrderRepository(db_session)
        with pytest.raises(NotImplementedError):
            await repo.delete(1)
