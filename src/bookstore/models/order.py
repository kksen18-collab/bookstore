"""Pydantic schemas for Order API boundary."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from bookstore.db_models import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for an item within an order creation request."""

    book_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr
    items: tuple[OrderItemCreate, ...] = Field(min_length=1)


class OrderUpdate(BaseModel):
    """Schema for updating an order status."""

    status: OrderStatus


class OrderItemResponse(BaseModel):
    """Schema for order item API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    """Schema for order API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_email: str
    status: OrderStatus
    total_amount: Decimal
    items: tuple[OrderItemResponse, ...]
    created_at: datetime.datetime
