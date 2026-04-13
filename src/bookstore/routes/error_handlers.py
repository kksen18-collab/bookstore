"""Global exception handlers mapping domain exceptions to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bookstore.exceptions import (
    BookstoreError,
    DuplicateISBNError,
    InvalidOrderStateError,
    NotFoundError,
    OutOfStockError,
)


def register_error_handlers(app: FastAPI) -> None:
    """Register all domain exception to HTTP response mappings."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle entity not found errors."""
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(OutOfStockError)
    async def out_of_stock_handler(_request: Request, exc: OutOfStockError) -> JSONResponse:
        """Handle out of stock errors."""
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(DuplicateISBNError)
    async def duplicate_isbn_handler(_request: Request, exc: DuplicateISBNError) -> JSONResponse:
        """Handle duplicate ISBN errors."""
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(InvalidOrderStateError)
    async def invalid_state_handler(_request: Request, exc: InvalidOrderStateError) -> JSONResponse:
        """Handle invalid order state transition errors."""
        return JSONResponse(status_code=422, content={"detail": exc.message})

    @app.exception_handler(BookstoreError)
    async def generic_handler(_request: Request, exc: BookstoreError) -> JSONResponse:
        """Handle generic bookstore domain errors."""
        return JSONResponse(status_code=400, content={"detail": exc.message})
