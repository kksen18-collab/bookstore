"""Integration tests for Order API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_author(client: AsyncClient) -> int:
    """Helper to create an author and return its ID."""
    resp = await client.post("/api/v1/authors/", json={"name": "Test Author"})
    return resp.json()["id"]


async def _create_book(client: AsyncClient, author_id: int, isbn: str = "9781234567890", stock: int = 10) -> int:
    """Helper to create a book and return its ID."""
    resp = await client.post(
        "/api/v1/books/",
        json={
            "title": "Test Book",
            "isbn": isbn,
            "price": "25.00",
            "stock_quantity": stock,
            "author_id": author_id,
        },
    )
    return resp.json()["id"]


@pytest.mark.integration
class TestOrdersAPI:
    """Integration tests for /api/v1/orders/ endpoints."""

    async def test_create_order(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        response = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 2}],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "John Doe"
        assert data["status"] == "pending"
        assert data["total_amount"] == "50.00"
        assert len(data["items"]) == 1

    async def test_create_order_decrements_stock(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id, stock=10)

        await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 3}],
            },
        )

        book_resp = await client.get(f"/api/v1/books/{book_id}")
        assert book_resp.json()["stock_quantity"] == 7

    async def test_create_order_out_of_stock(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id, stock=1)

        response = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 5}],
            },
        )
        assert response.status_code == 409

    async def test_create_order_nonexistent_book(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": 9999, "quantity": 1}],
            },
        )
        assert response.status_code == 404

    async def test_get_order(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        create_resp = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 1}],
            },
        )
        order_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    async def test_get_nonexistent_order(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/orders/9999")
        assert response.status_code == 404

    async def test_list_orders(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 1}],
            },
        )

        response = await client.get("/api/v1/orders/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_update_order_status(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        create_resp = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 1}],
            },
        )
        order_id = create_resp.json()["id"]

        response = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "confirmed"})
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

    async def test_invalid_status_transition(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        create_resp = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 1}],
            },
        )
        order_id = create_resp.json()["id"]

        response = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "delivered"})
        assert response.status_code == 422

    async def test_full_order_lifecycle(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        book_id = await _create_book(client, author_id)

        create_resp = await client.post(
            "/api/v1/orders/",
            json={
                "customer_name": "John",
                "customer_email": "john@example.com",
                "items": [{"book_id": book_id, "quantity": 1}],
            },
        )
        order_id = create_resp.json()["id"]

        resp = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "confirmed"})
        assert resp.status_code == 200

        resp = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "shipped"})
        assert resp.status_code == 200

        resp = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "delivered"})
        assert resp.status_code == 200
