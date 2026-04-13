"""Integration tests for Book API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


async def _create_author(client: AsyncClient) -> int:
    """Helper to create an author and return its ID."""
    resp = await client.post("/api/v1/authors/", json={"name": "Test Author"})
    return resp.json()["id"]


@pytest.mark.integration
class TestBooksAPI:
    """Integration tests for /api/v1/books/ endpoints."""

    async def test_create_book(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        response = await client.post(
            "/api/v1/books/",
            json={
                "title": "Test Book",
                "isbn": "9781234567890",
                "price": "19.99",
                "stock_quantity": 10,
                "author_id": author_id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["isbn"] == "9781234567890"
        assert data["author"]["id"] == author_id

    async def test_create_book_nonexistent_author(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/books/",
            json={
                "title": "Test Book",
                "isbn": "9781234567890",
                "price": "19.99",
                "author_id": 9999,
            },
        )
        assert response.status_code == 404

    async def test_create_book_duplicate_isbn(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        await client.post(
            "/api/v1/books/",
            json={"title": "Book 1", "isbn": "9781234567890", "price": "10.00", "author_id": author_id},
        )
        response = await client.post(
            "/api/v1/books/",
            json={"title": "Book 2", "isbn": "9781234567890", "price": "20.00", "author_id": author_id},
        )
        assert response.status_code == 409

    async def test_get_book(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        create_resp = await client.post(
            "/api/v1/books/",
            json={"title": "Test Book", "isbn": "9781234567890", "price": "19.99", "author_id": author_id},
        )
        book_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Book"

    async def test_get_nonexistent_book(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/books/9999")
        assert response.status_code == 404

    async def test_list_books(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        await client.post(
            "/api/v1/books/",
            json={"title": "Book 1", "isbn": "9781234567891", "price": "10.00", "author_id": author_id},
        )
        await client.post(
            "/api/v1/books/",
            json={"title": "Book 2", "isbn": "9781234567892", "price": "20.00", "author_id": author_id},
        )

        response = await client.get("/api/v1/books/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    async def test_update_book(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        create_resp = await client.post(
            "/api/v1/books/",
            json={"title": "Old Title", "isbn": "9781234567890", "price": "19.99", "author_id": author_id},
        )
        book_id = create_resp.json()["id"]

        response = await client.patch(f"/api/v1/books/{book_id}", json={"title": "New Title"})
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    async def test_delete_book(self, client: AsyncClient) -> None:
        author_id = await _create_author(client)
        create_resp = await client.post(
            "/api/v1/books/",
            json={"title": "To Delete", "isbn": "9781234567890", "price": "10.00", "author_id": author_id},
        )
        book_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/books/{book_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/v1/books/{book_id}")
        assert get_resp.status_code == 404
