"""API routes for Order operations."""

from __future__ import annotations

from fastapi import APIRouter, Query

from bookstore.dependencies import OrderServiceDep
from bookstore.models.order import OrderCreate, OrderResponse, OrderUpdate
from bookstore.models.pagination import PaginatedResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    service: OrderServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[OrderResponse]:
    """List all orders with pagination."""
    orders, total = await service.list_orders(offset=offset, limit=limit)
    return PaginatedResponse(
        items=tuple(OrderResponse.model_validate(o) for o in orders),
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    """Retrieve a single order by ID."""
    order = await service.get_order(order_id)
    return OrderResponse.model_validate(order)


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, service: OrderServiceDep) -> OrderResponse:
    """Create a new order."""
    order = await service.create_order(data)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order_status(order_id: int, data: OrderUpdate, service: OrderServiceDep) -> OrderResponse:
    """Update an order's status."""
    order = await service.update_order_status(order_id, data)
    return OrderResponse.model_validate(order)
