"use strict";

/**
 * Bookstore API client.
 *
 * The API base URL defaults to http://localhost:8000/api/v1.
 * Override it before loading this script by setting window.BOOKSTORE_API_URL.
 */
const API_BASE_URL =
    (typeof window !== "undefined" && window.BOOKSTORE_API_URL) ||
    "http://localhost:8000/api/v1";

/**
 * Represents an HTTP error returned by the API.
 */
class ApiError extends Error {
    /**
     * @param {number} status - HTTP status code
     * @param {string} message - Human-readable error description
     */
    constructor(status, message) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

/**
 * Generic fetch wrapper that handles JSON parsing and API error mapping.
 *
 * @param {string} path - API path relative to the base URL (e.g. "/authors/")
 * @param {RequestInit} [options] - Fetch options (method, body, headers, …)
 * @returns {Promise<any>} Parsed JSON response, or null for 204 No Content
 * @throws {ApiError} When the server returns a non-2xx status code
 */
async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
    });

    if (!response.ok) {
        const payload = await response.json().catch(() => ({ detail: response.statusText }));
        const detail = payload.detail || `HTTP ${response.status}`;
        const message = typeof detail === "string" ? detail : JSON.stringify(detail);
        throw new ApiError(response.status, message);
    }

    if (response.status === 204) return null;
    return response.json();
}

/** Authors REST endpoints. */
const authorsApi = {
    /** @param {number} [offset] @param {number} [limit] */
    list: (offset = 0, limit = 20) => apiFetch(`/authors/?offset=${offset}&limit=${limit}`),
    /** @param {number} id */
    get: (id) => apiFetch(`/authors/${id}`),
    /** @param {{ name: string, bio?: string }} data */
    create: (data) => apiFetch("/authors/", { method: "POST", body: JSON.stringify(data) }),
    /** @param {number} id @param {{ name?: string, bio?: string }} data */
    update: (id, data) => apiFetch(`/authors/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    /** @param {number} id */
    delete: (id) => apiFetch(`/authors/${id}`, { method: "DELETE" }),
};

/** Books REST endpoints. */
const booksApi = {
    /** @param {number} [offset] @param {number} [limit] */
    list: (offset = 0, limit = 20) => apiFetch(`/books/?offset=${offset}&limit=${limit}`),
    /** @param {number} id */
    get: (id) => apiFetch(`/books/${id}`),
    /** @param {{ title: string, isbn: string, price: string, stock_quantity: number, author_id: number }} data */
    create: (data) => apiFetch("/books/", { method: "POST", body: JSON.stringify(data) }),
    /** @param {number} id @param {object} data */
    update: (id, data) => apiFetch(`/books/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    /** @param {number} id */
    delete: (id) => apiFetch(`/books/${id}`, { method: "DELETE" }),
};

/** Orders REST endpoints. */
const ordersApi = {
    /** @param {number} [offset] @param {number} [limit] */
    list: (offset = 0, limit = 20) => apiFetch(`/orders/?offset=${offset}&limit=${limit}`),
    /** @param {number} id */
    get: (id) => apiFetch(`/orders/${id}`),
    /**
     * @param {{ customer_name: string, customer_email: string,
     *            items: Array<{ book_id: number, quantity: number }> }} data
     */
    create: (data) => apiFetch("/orders/", { method: "POST", body: JSON.stringify(data) }),
    /**
     * @param {number} id
     * @param {"pending"|"confirmed"|"shipped"|"delivered"|"cancelled"} status
     */
    updateStatus: (id, status) =>
        apiFetch(`/orders/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
};
