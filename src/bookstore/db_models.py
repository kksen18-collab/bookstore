"""SQLAlchemy ORM models for the bookstore database."""

from __future__ import annotations

import datetime
import enum
from decimal import Decimal

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class OrderStatus(enum.StrEnum):
    """Status progression for an order."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class AuthorORM(Base):
    """ORM model for the authors table."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(insert_default=lambda: datetime.datetime.now(datetime.UTC))

    books: Mapped[list[BookORM]] = relationship(back_populates="author", lazy="selectin")


class BookORM(Base):
    """ORM model for the books table."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock_quantity: Mapped[int] = mapped_column(default=0)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(insert_default=lambda: datetime.datetime.now(datetime.UTC))

    author: Mapped[AuthorORM] = relationship(back_populates="books", lazy="selectin")
    order_items: Mapped[list[OrderItemORM]] = relationship(back_populates="book")


class OrderORM(Base):
    """ORM model for the orders table."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(255))
    customer_email: Mapped[str] = mapped_column(String(255))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, native_enum=False),
        default=OrderStatus.PENDING,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime.datetime] = mapped_column(insert_default=lambda: datetime.datetime.now(datetime.UTC))

    items: Mapped[list[OrderItemORM]] = relationship(
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class OrderItemORM(Base):
    """ORM model for the order_items table."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped[OrderORM] = relationship(back_populates="items")
    book: Mapped[BookORM] = relationship(back_populates="order_items", lazy="selectin")
