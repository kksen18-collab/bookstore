# Bookstore API

A RESTful bookstore API built with FastAPI, SQLAlchemy (async), and Pydantic v2. Manages authors, books, and orders with stock management and order lifecycle tracking.

## Stack

- **Python 3.13+**
- **FastAPI** — async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** (async) + **aiosqlite** — async ORM with SQLite
- **Pydantic v2** — request/response validation
- **uv** — package manager
- **pytest** — testing with async support

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI Routes                    │
│           /api/v1/authors, /books, /orders           │
├─────────────────────────────────────────────────────┤
│                   Service Layer                      │
│     AuthorService · BookService · OrderService       │
│         (business logic, validation, stock mgmt)     │
├─────────────────────────────────────────────────────┤
│                 Repository Layer                     │
│   AuthorRepository · BookRepository · OrderRepository│
│           (data access, SQLAlchemy queries)           │
├─────────────────────────────────────────────────────┤
│                 SQLAlchemy ORM Models                 │
│     AuthorORM · BookORM · OrderORM · OrderItemORM    │
├─────────────────────────────────────────────────────┤
│                   SQLite Database                    │
└─────────────────────────────────────────────────────┘
```

**Dependency direction:** Routes → Services → Repositories → ORM Models

- **Dependency injection** via FastAPI's `Depends` — repositories are injected into services, services into route handlers
- **ABC interfaces** for repositories — enables clean mocking in unit tests
- **Transaction-per-request** — each HTTP request runs in a single database transaction (auto-commit on success, rollback on error)
- **Domain exceptions** — custom exception hierarchy mapped to HTTP status codes

## Project Structure

```
bookstore/
├── pyproject.toml                          # deps, tool config, metadata
├── uv.lock                                 # locked dependencies
├── .gitignore
├── README.md
├── src/
│   └── bookstore/
│       ├── __init__.py
│       ├── main.py                         # FastAPI app factory & lifespan
│       ├── config.py                       # Settings via pydantic-settings
│       ├── database.py                     # Async engine & session management
│       ├── db_models.py                    # SQLAlchemy ORM models
│       ├── dependencies.py                 # FastAPI DI wiring
│       ├── exceptions.py                   # Domain exception hierarchy
│       ├── models/                         # Pydantic schemas (API boundary)
│       │   ├── author.py                   #   AuthorCreate, AuthorUpdate, AuthorResponse
│       │   ├── book.py                     #   BookCreate, BookUpdate, BookResponse
│       │   ├── order.py                    #   OrderCreate, OrderUpdate, OrderResponse
│       │   └── pagination.py               #   PaginatedResponse[T]
│       ├── repositories/                   # Data access layer
│       │   ├── base.py                     #   ABC BaseRepository
│       │   ├── author.py                   #   AuthorRepository
│       │   ├── book.py                     #   BookRepository
│       │   └── order.py                    #   OrderRepository
│       ├── routes/                         # API route handlers
│       │   ├── authors.py                  #   /api/v1/authors
│       │   ├── books.py                    #   /api/v1/books
│       │   ├── orders.py                   #   /api/v1/orders
│       │   └── error_handlers.py           #   Exception → HTTP mapping
│       ├── services/                       # Business logic
│       │   ├── author.py                   #   AuthorService
│       │   ├── book.py                     #   BookService
│       │   └── order.py                    #   OrderService
│       └── utils/
└── tests/
    ├── conftest.py                         # Shared fixtures (in-memory DB, test client)
    ├── unit/                               # Unit tests (mocked dependencies)
    │   ├── test_config.py
    │   ├── test_database.py
    │   ├── test_dependencies.py
    │   ├── test_exceptions.py
    │   ├── test_models.py
    │   ├── test_services_author.py
    │   ├── test_services_book.py
    │   └── test_services_order.py
    └── integration/                        # Integration tests (real DB & HTTP)
        ├── test_authors_api.py
        ├── test_books_api.py
        ├── test_orders_api.py
        └── test_repositories.py
```

## Setup

```bash
# Install dependencies
uv sync

# Run the API server
uv run uvicorn bookstore.main:app --reload

# Open Swagger UI
# http://127.0.0.1:8000/docs
```

## API Endpoints

All endpoints are under `/api/v1/`.

### Authors

| Method | Path                | Description          | Status Codes   |
|--------|---------------------|----------------------|----------------|
| GET    | `/authors/`         | List authors (paginated) | 200        |
| POST   | `/authors/`         | Create an author     | 201            |
| GET    | `/authors/{id}`     | Get author by ID     | 200, 404       |
| PATCH  | `/authors/{id}`     | Update an author     | 200, 404       |
| DELETE | `/authors/{id}`     | Delete an author     | 204, 404       |

### Books

| Method | Path              | Description           | Status Codes       |
|--------|-------------------|-----------------------|--------------------|
| GET    | `/books/`         | List books (paginated)| 200                |
| POST   | `/books/`         | Create a book         | 201, 404, 409      |
| GET    | `/books/{id}`     | Get book by ID        | 200, 404           |
| PATCH  | `/books/{id}`     | Update a book         | 200, 404, 409      |
| DELETE | `/books/{id}`     | Delete a book         | 204, 404           |

- **404** — author not found (on create/update with invalid `author_id`)
- **409** — duplicate ISBN

### Orders

| Method | Path               | Description           | Status Codes       |
|--------|--------------------|-----------------------|--------------------|
| GET    | `/orders/`         | List orders (paginated)| 200               |
| POST   | `/orders/`         | Create an order       | 201, 404, 409      |
| GET    | `/orders/{id}`     | Get order by ID       | 200, 404           |
| PATCH  | `/orders/{id}`     | Update order status   | 200, 404, 422      |

- **404** — book not found in order items
- **409** — insufficient stock
- **422** — invalid status transition

### Order Status Lifecycle

```
pending ──→ confirmed ──→ shipped ──→ delivered
  │              │
  └──→ cancelled ←┘
```

Orders cannot be deleted — they can only be cancelled.

### Pagination

All list endpoints support pagination via query parameters:

```
GET /api/v1/authors/?offset=0&limit=20
```

Response:
```json
{
  "items": [...],
  "total": 42,
  "offset": 0,
  "limit": 20
}
```

## Example Requests

```bash
# Create an author
curl -X POST http://localhost:8000/api/v1/authors/ \
  -H "Content-Type: application/json" \
  -d '{"name": "George Orwell", "bio": "English novelist and essayist"}'

# Create a book
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Content-Type: application/json" \
  -d '{"title": "1984", "isbn": "9780451524935", "price": "9.99", "stock_quantity": 50, "author_id": 1}'

# Create an order
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Jane Doe", "customer_email": "jane@example.com", "items": [{"book_id": 1, "quantity": 2}]}'

# Confirm the order
curl -X PATCH http://localhost:8000/api/v1/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

## Commands

```bash
# Install / sync dependencies
uv sync

# Run the dev server
uv run uvicorn bookstore.main:app --reload

# Run all tests with coverage
uv run pytest tests/ -v --tb=short --cov --cov-report=term-missing

# Run a single test
uv run pytest tests/ -k "test_name"

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Lint
uv run ruff check . --fix

# Format
uv run ruff format .

# Type check
uv run mypy src/
```

## Configuration

Configuration is loaded from environment variables with the `BOOKSTORE_` prefix, or from a `.env` file.

| Variable                | Default                              | Description          |
|-------------------------|--------------------------------------|----------------------|
| `BOOKSTORE_DATABASE_URL`| `sqlite+aiosqlite:///./bookstore.db` | Database connection  |
| `BOOKSTORE_DEBUG`       | `false`                              | Enable SQL echo      |
| `BOOKSTORE_APP_TITLE`   | `Bookstore API`                      | OpenAPI title        |
| `BOOKSTORE_APP_VERSION` | `0.1.0`                              | OpenAPI version      |

## Database Schema

```
┌──────────────┐       ┌──────────────┐
│   authors    │       │    books     │
├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │
│ name         │  │    │ title        │
│ bio          │  └───→│ author_id(FK)│
│ created_at   │       │ isbn (unique)│
└──────────────┘       │ price        │
                       │ stock_quantity│
                       │ created_at   │
                       └──────┬───────┘
                              │
┌──────────────┐       ┌──────┴───────┐
│   orders     │       │ order_items  │
├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │
│ customer_name│  └───→│ order_id(FK) │
│ customer_email│      │ book_id (FK) │←─┘
│ status       │       │ quantity     │
│ total_amount │       │ unit_price   │
│ created_at   │       └──────────────┘
└──────────────┘
```
