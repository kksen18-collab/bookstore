"""API routes for Book operations."""

from __future__ import annotations

from fastapi import APIRouter, Query

from bookstore.dependencies import BookServiceDep
from bookstore.models.book import BookCreate, BookResponse, BookUpdate
from bookstore.models.pagination import PaginatedResponse

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=PaginatedResponse[BookResponse])
async def list_books(
    service: BookServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[BookResponse]:
    """List all books with pagination."""
    books, total = await service.list_books(offset=offset, limit=limit)
    return PaginatedResponse(
        items=tuple(BookResponse.model_validate(b) for b in books),
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, service: BookServiceDep) -> BookResponse:
    """Retrieve a single book by ID."""
    book = await service.get_book(book_id)
    return BookResponse.model_validate(book)


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(data: BookCreate, service: BookServiceDep) -> BookResponse:
    """Create a new book."""
    book = await service.create_book(data)
    return BookResponse.model_validate(book)


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, data: BookUpdate, service: BookServiceDep) -> BookResponse:
    """Partially update a book."""
    book = await service.update_book(book_id, data)
    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    """Delete a book."""
    await service.delete_book(book_id)
