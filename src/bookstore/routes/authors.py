"""API routes for Author operations."""

from __future__ import annotations

from fastapi import APIRouter, Query

from bookstore.dependencies import AuthorServiceDep
from bookstore.models.author import AuthorCreate, AuthorResponse, AuthorUpdate
from bookstore.models.pagination import PaginatedResponse

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=PaginatedResponse[AuthorResponse])
async def list_authors(
    service: AuthorServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[AuthorResponse]:
    """List all authors with pagination."""
    authors, total = await service.list_authors(offset=offset, limit=limit)
    return PaginatedResponse(
        items=tuple(AuthorResponse.model_validate(a) for a in authors),
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, service: AuthorServiceDep) -> AuthorResponse:
    """Retrieve a single author by ID."""
    author = await service.get_author(author_id)
    return AuthorResponse.model_validate(author)


@router.post("/", response_model=AuthorResponse, status_code=201)
async def create_author(data: AuthorCreate, service: AuthorServiceDep) -> AuthorResponse:
    """Create a new author."""
    author = await service.create_author(data)
    return AuthorResponse.model_validate(author)


@router.patch("/{author_id}", response_model=AuthorResponse)
async def update_author(author_id: int, data: AuthorUpdate, service: AuthorServiceDep) -> AuthorResponse:
    """Partially update an author."""
    author = await service.update_author(author_id, data)
    return AuthorResponse.model_validate(author)


@router.delete("/{author_id}", status_code=204)
async def delete_author(author_id: int, service: AuthorServiceDep) -> None:
    """Delete an author."""
    await service.delete_author(author_id)
