"""Integration tests for Author API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestAuthorsAPI:
    """Integration tests for /api/v1/authors/ endpoints."""

    async def test_create_author(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/authors/", json={"name": "Jane Doe", "bio": "A great author"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["bio"] == "A great author"
        assert "id" in data

    async def test_get_author(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/authors/", json={"name": "Jane Doe"})
        author_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/authors/{author_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Jane Doe"

    async def test_get_nonexistent_author(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/authors/9999")
        assert response.status_code == 404

    async def test_list_authors(self, client: AsyncClient) -> None:
        await client.post("/api/v1/authors/", json={"name": "Author One"})
        await client.post("/api/v1/authors/", json={"name": "Author Two"})

        response = await client.get("/api/v1/authors/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    async def test_list_authors_pagination(self, client: AsyncClient) -> None:
        for i in range(5):
            await client.post("/api/v1/authors/", json={"name": f"Author {i}"})

        response = await client.get("/api/v1/authors/?offset=0&limit=2")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5

    async def test_update_author(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/authors/", json={"name": "Old Name"})
        author_id = create_resp.json()["id"]

        response = await client.patch(f"/api/v1/authors/{author_id}", json={"name": "New Name"})
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    async def test_update_nonexistent_author(self, client: AsyncClient) -> None:
        response = await client.patch("/api/v1/authors/9999", json={"name": "Test"})
        assert response.status_code == 404

    async def test_delete_author(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/authors/", json={"name": "To Delete"})
        author_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/authors/{author_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/v1/authors/{author_id}")
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_author(self, client: AsyncClient) -> None:
        response = await client.delete("/api/v1/authors/9999")
        assert response.status_code == 404
