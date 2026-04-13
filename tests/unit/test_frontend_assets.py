"""Unit tests for frontend asset structure and content.

These tests verify that the frontend files exist, are properly structured,
and contain the expected identifiers — without requiring a running browser
or JavaScript runtime.
"""

from __future__ import annotations

import pathlib

import pytest

FRONTEND_DIR = pathlib.Path(__file__).parents[2] / "frontend"
JS_DIR = FRONTEND_DIR / "js"
CSS_DIR = FRONTEND_DIR / "css"


class TestFrontendStructure:
    """Tests that verify the frontend directory and file layout."""

    def test_frontend_directory_exists(self) -> None:
        """Frontend directory must exist at the project root."""
        assert FRONTEND_DIR.is_dir(), "frontend/ directory not found at project root"

    def test_index_html_exists(self) -> None:
        """Main HTML entry point must exist."""
        assert (FRONTEND_DIR / "index.html").is_file()

    def test_css_directory_exists(self) -> None:
        """CSS subdirectory must exist."""
        assert CSS_DIR.is_dir()

    def test_style_css_exists(self) -> None:
        """Primary stylesheet must exist."""
        assert (CSS_DIR / "style.css").is_file()

    def test_js_directory_exists(self) -> None:
        """JS subdirectory must exist."""
        assert JS_DIR.is_dir()

    def test_api_js_exists(self) -> None:
        """API client script must exist."""
        assert (JS_DIR / "api.js").is_file()

    def test_app_js_exists(self) -> None:
        """Application logic script must exist."""
        assert (JS_DIR / "app.js").is_file()

    def test_frontend_files_are_non_empty(self) -> None:
        """All frontend files must have content."""
        for path in [
            FRONTEND_DIR / "index.html",
            CSS_DIR / "style.css",
            JS_DIR / "api.js",
            JS_DIR / "app.js",
        ]:
            assert path.stat().st_size > 0, f"{path.name} is empty"


class TestIndexHtmlContent:
    """Tests that verify index.html contains required structural elements."""

    @pytest.fixture(scope="class")
    def html(self) -> str:
        """Read index.html once for all tests in this class."""
        return (FRONTEND_DIR / "index.html").read_text()

    def test_has_doctype(self, html: str) -> None:
        """HTML must declare a DOCTYPE."""
        assert html.strip().lower().startswith("<!doctype html")

    def test_has_viewport_meta(self, html: str) -> None:
        """HTML must include a responsive viewport meta tag."""
        assert "viewport" in html

    def test_has_books_section(self, html: str) -> None:
        """HTML must reference the books tab/section."""
        assert "books" in html.lower()

    def test_has_authors_section(self, html: str) -> None:
        """HTML must reference the authors tab/section."""
        assert "authors" in html.lower()

    def test_has_orders_section(self, html: str) -> None:
        """HTML must reference the orders tab/section."""
        assert "orders" in html.lower()

    def test_loads_api_script(self, html: str) -> None:
        """HTML must load the API client script."""
        assert "api.js" in html

    def test_loads_app_script(self, html: str) -> None:
        """HTML must load the application logic script."""
        assert "app.js" in html

    def test_links_stylesheet(self, html: str) -> None:
        """HTML must link the CSS stylesheet."""
        assert "style.css" in html

    def test_has_modal(self, html: str) -> None:
        """HTML must contain a modal element for create/edit forms."""
        assert "modal" in html.lower()

    def test_has_toast(self, html: str) -> None:
        """HTML must contain a toast/notification element."""
        assert "toast" in html.lower()


class TestApiJsContent:
    """Tests that verify api.js exposes the expected API namespaces and utilities."""

    @pytest.fixture(scope="class")
    def src(self) -> str:
        """Read api.js once for all tests in this class."""
        return (JS_DIR / "api.js").read_text()

    def test_api_error_class_defined(self, src: str) -> None:
        """ApiError custom error class must be present."""
        assert "ApiError" in src

    def test_api_base_url_configurable(self, src: str) -> None:
        """API base URL must be overridable via window.BOOKSTORE_API_URL."""
        assert "BOOKSTORE_API_URL" in src

    def test_authors_api_namespace(self, src: str) -> None:
        """authorsApi namespace must be declared."""
        assert "authorsApi" in src

    def test_books_api_namespace(self, src: str) -> None:
        """booksApi namespace must be declared."""
        assert "booksApi" in src

    def test_orders_api_namespace(self, src: str) -> None:
        """ordersApi namespace must be declared."""
        assert "ordersApi" in src

    def test_authors_api_has_list(self, src: str) -> None:
        """authorsApi must expose a list function."""
        assert "list" in src

    def test_authors_api_has_create(self, src: str) -> None:
        """authorsApi must expose a create function."""
        assert "create" in src

    def test_authors_api_has_update(self, src: str) -> None:
        """authorsApi must expose an update function."""
        assert "update" in src

    def test_authors_api_has_delete(self, src: str) -> None:
        """authorsApi must expose a delete function."""
        assert "delete" in src

    def test_orders_api_has_update_status(self, src: str) -> None:
        """ordersApi must expose an updateStatus function."""
        assert "updateStatus" in src


class TestAppJsContent:
    """Tests that verify app.js contains the expected UI functions."""

    @pytest.fixture(scope="class")
    def src(self) -> str:
        """Read app.js once for all tests in this class."""
        return (JS_DIR / "app.js").read_text()

    def test_has_load_books(self, src: str) -> None:
        """loadBooks function must be defined."""
        assert "loadBooks" in src

    def test_has_load_authors(self, src: str) -> None:
        """loadAuthors function must be defined."""
        assert "loadAuthors" in src

    def test_has_load_orders(self, src: str) -> None:
        """loadOrders function must be defined."""
        assert "loadOrders" in src

    def test_has_show_toast(self, src: str) -> None:
        """showToast utility must be present."""
        assert "showToast" in src

    def test_has_escape_html(self, src: str) -> None:
        """escapeHtml XSS-prevention utility must be present."""
        assert "escapeHtml" in src

    def test_has_open_modal(self, src: str) -> None:
        """openModal function must be present."""
        assert "openModal" in src

    def test_has_close_modal(self, src: str) -> None:
        """closeModal function must be present."""
        assert "closeModal" in src

    def test_has_render_pagination(self, src: str) -> None:
        """renderPagination function must be present."""
        assert "renderPagination" in src

    def test_has_switch_tab(self, src: str) -> None:
        """switchTab function must be present."""
        assert "switchTab" in src

    def test_has_dom_content_loaded_listener(self, src: str) -> None:
        """DOMContentLoaded listener must wire up all event handlers."""
        assert "DOMContentLoaded" in src

    def test_order_statuses_defined(self, src: str) -> None:
        """ORDER_STATUSES constant must list valid order states."""
        for status in ("pending", "confirmed", "shipped", "delivered", "cancelled"):
            assert status in src
