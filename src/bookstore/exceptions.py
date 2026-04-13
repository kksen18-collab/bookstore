"""Domain-specific exception hierarchy for the bookstore."""

from __future__ import annotations


class BookstoreError(Exception):
    """Base exception for all bookstore domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(BookstoreError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity: str, entity_id: int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id {entity_id} not found")


class OutOfStockError(BookstoreError):
    """Raised when a book does not have sufficient stock."""

    def __init__(self, book_id: int, requested: int, available: int) -> None:
        self.book_id = book_id
        self.requested = requested
        self.available = available
        super().__init__(f"Book {book_id}: requested {requested}, available {available}")


class DuplicateISBNError(BookstoreError):
    """Raised when attempting to create a book with a duplicate ISBN."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"Book with ISBN {isbn} already exists")


class InvalidOrderStateError(BookstoreError):
    """Raised when an order state transition is invalid."""

    def __init__(self, current_status: str, target_status: str) -> None:
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(f"Cannot transition order from {current_status} to {target_status}")
