# CLAUDE.md

You are working in a professional Python data engineering codebase. Follow every instruction below exactly. When in doubt, ask before acting.

## Identity & Stack

Python 3.13+ · uv package manager · pyproject.toml (PEP 621) · Pydantic v2 · pytest · GitHub

## Commands

```bash
uv sync                          # install/sync dependencies
uv run pytest tests/ -v --tb=short --cov --cov-report=term-missing  # test with coverage
uv run pytest tests/ -k "test_name"                                  # run single test
uv run ruff check . --fix        # lint
uv run ruff format .             # format
uv run mypy src/                 # type check
uv run python -m src.main        # run entrypoint
```

## Project Layout

```
project-root/
├── CLAUDE.md
├── pyproject.toml               # single source of truth for deps, tools, metadata
├── uv.lock                      # DO NOT edit manually
├── .claude/
│   └── rules/                   # path-scoped rules (auto-loaded by Claude Code)
│       ├── models.md            # Pydantic patterns — src/**/models/**
│       ├── oop.md               # OOP / dataclass / decorator patterns — src/**/*.py
│       ├── testing.md           # pytest conventions — tests/**
│       └── repositories.md     # data access patterns — src/**/repositories/**
├── src/
│   └── <package>/
│       ├── __init__.py
│       ├── main.py              # entrypoint
│       ├── models/              # Pydantic models
│       ├── services/            # business logic (OOP classes)
│       ├── repositories/        # data access layer
│       ├── utils/               # pure helpers, decorators
│       └── config.py            # Settings via pydantic-settings
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── unit/                    # mirrors src/ structure
│   └── integration/             # real service tests (marked)
├── .github/
│   └── workflows/               # CI pipelines
└── docs/
```

## Code Standards

<important>
NEVER skip type hints. Every function signature must have full parameter and return type annotations — no exceptions.
Every function and method MUST have unit tests. Target ≥90% line coverage; strive for 100%.
</important>

- **PEP 8 + latest PEP standards** — enforced via ruff. Line length 120.
- **Type hints everywhere** — use `from __future__ import annotations` at the top of every module.
- **Pydantic v2** for external boundaries (API payloads, configs, DTOs). **`@dataclass`** for internal domain objects and value types. See `.claude/rules/models.md`.
- **OOP by default** — dependency injection, ABC interfaces, composition over inheritance. Full OOP toolkit: `@property`, `@cached_property`, `@staticmethod`, `@classmethod`, context managers, custom decorators. See `.claude/rules/oop.md`.
- **Testing** — pytest only, ≥90% coverage, mock at boundaries. See `.claude/rules/testing.md`.
- **Modular design** — one responsibility per module. No file >300 lines. Methods >40 lines need decomposition.
- **Docstrings** — Google style on every public class and method.
- **Immutability** — prefer `tuple` over `list`, `frozenset` over `set`, `Literal` over magic strings.
- **Enums** — `StrEnum` (Python 3.11+) for string constants in branching logic.
- **Error handling** — domain-specific exceptions from a project base. Never bare `except:`. Use `logging`, never `print`.
- **f-strings** preferred. **Absolute imports** only (stdlib → third-party → local, enforced by ruff isort).

## pyproject.toml Conventions

- Build backend: `hatchling` or `setuptools`.
- All tool config in `pyproject.toml` — ruff, mypy, pytest, coverage. No `.cfg` or `.ini` files.
- Pin direct deps to compatible ranges (`>=1.2,<2`). `uv.lock` pins transitive deps.
- Dev dependencies under `[dependency-groups]` → `dev = [...]`.

## Git & GitHub

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- Branch naming: `feat/<slug>`, `fix/<slug>`, `refactor/<slug>`.
- PRs require passing CI (lint + type-check + tests + coverage gate).
- Never commit secrets, `.env` files, or `uv.lock` editor artifacts.
- `.gitignore`: `__pycache__/`, `.venv/`, `*.pyc`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `.env`.

## When Compacting

Always preserve: the full list of modified files, all test commands, any failing test names, and the current branch/task context.

## What NOT To Do

- Do NOT create `requirements.txt` — use `uv` + `pyproject.toml` exclusively.
- Do NOT use `Any` type — find or create the proper type.
- Do NOT use `dict` as a data container when a Pydantic model or dataclass fits.
- Do NOT write functions longer than 40 lines without decomposing.
- Do NOT skip tests for "simple" functions — every function gets tested.
- Do NOT use `os.path` — use `pathlib.Path`.
- Do NOT add dependencies without confirming need and using `uv add`.