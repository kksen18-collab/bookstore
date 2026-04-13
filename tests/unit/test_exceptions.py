"""Tests for the domain exception hierarchy."""

from __future__ import annotations

from bookstore.exceptions import (
    BookstoreError,
    DuplicateISBNError,
    InvalidOrderStateError,
    NotFoundError,
    OutOfStockError,
)


class TestBookstoreError:
    """Tests for the base BookstoreError."""

    def test_message(self) -> None:
        err = BookstoreError("something went wrong")
        assert err.message == "something went wrong"
        assert str(err) == "something went wrong"

    def test_is_exception(self) -> None:
        assert issubclass(BookstoreError, Exception)


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_message_format(self) -> None:
        err = NotFoundError("Book", 42)
        assert err.message == "Book with id 42 not found"
        assert err.entity == "Book"
        assert err.entity_id == 42

    def test_inherits_bookstore_error(self) -> None:
        err = NotFoundError("Author", 1)
        assert isinstance(err, BookstoreError)


class TestOutOfStockError:
    """Tests for OutOfStockError."""

    def test_message_format(self) -> None:
        err = OutOfStockError(book_id=5, requested=10, available=3)
        assert err.message == "Book 5: requested 10, available 3"
        assert err.book_id == 5
        assert err.requested == 10
        assert err.available == 3

    def test_inherits_bookstore_error(self) -> None:
        assert issubclass(OutOfStockError, BookstoreError)


class TestDuplicateISBNError:
    """Tests for DuplicateISBNError."""

    def test_message_format(self) -> None:
        err = DuplicateISBNError("9781234567890")
        assert err.message == "Book with ISBN 9781234567890 already exists"
        assert err.isbn == "9781234567890"

    def test_inherits_bookstore_error(self) -> None:
        assert issubclass(DuplicateISBNError, BookstoreError)


class TestInvalidOrderStateError:
    """Tests for InvalidOrderStateError."""

    def test_message_format(self) -> None:
        err = InvalidOrderStateError("pending", "delivered")
        assert err.message == "Cannot transition order from pending to delivered"
        assert err.current_status == "pending"
        assert err.target_status == "delivered"

    def test_inherits_bookstore_error(self) -> None:
        assert issubclass(InvalidOrderStateError, BookstoreError)
