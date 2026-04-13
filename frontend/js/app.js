"use strict";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const state = {
    activeTab: "books",
    books:   { offset: 0, limit: 10, total: 0, items: [] },
    authors: { offset: 0, limit: 10, total: 0, items: [] },
    orders:  { offset: 0, limit: 10, total: 0, items: [] },
};

const ORDER_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"];

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

/** Escape a value for safe HTML insertion. */
function escapeHtml(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

/** Collect non-empty form fields as a plain object. */
function getFormData(formId) {
    const data = {};
    new FormData(document.getElementById(formId)).forEach((value, key) => {
        if (value !== "") data[key] = value;
    });
    return data;
}

/** Show a brief toast notification. */
function showToast(message, type = "success") {
    const el = document.getElementById("toast");
    el.textContent = message;
    el.className = `toast toast--${type}`;
    setTimeout(() => { el.className = "toast hidden"; }, 3500);
}

/** Render page-number buttons into a container. */
function renderPagination(containerId, offset, limit, total, onPage) {
    const container = document.getElementById(containerId);
    if (total <= limit) { container.innerHTML = ""; return; }
    const pages = Math.ceil(total / limit);
    const current = Math.floor(offset / limit);
    container.innerHTML = Array.from({ length: pages }, (_, i) => {
        const cls = i === current ? "pagination__btn pagination__btn--active" : "pagination__btn";
        return `<button class="${cls}" data-page="${i}">${i + 1}</button>`;
    }).join("");
    container.querySelectorAll(".pagination__btn").forEach((btn) => {
        btn.addEventListener("click", () => onPage(Number(btn.dataset.page) * limit));
    });
}

// ---------------------------------------------------------------------------
// Modal
// ---------------------------------------------------------------------------

let modalSubmitHandler = null;

/** Open the shared modal dialog with a custom body and submit callback. */
function openModal(title, bodyHtml, onSubmit) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").innerHTML = bodyHtml;
    document.getElementById("modal-overlay").classList.remove("hidden");
    document.getElementById("modal-submit").disabled = false;
    modalSubmitHandler = onSubmit;
}

/** Close the modal and clear state. */
function closeModal() {
    document.getElementById("modal-overlay").classList.add("hidden");
    modalSubmitHandler = null;
}

// ---------------------------------------------------------------------------
// Tab management
// ---------------------------------------------------------------------------

function switchTab(tabId) {
    document.querySelectorAll(".nav__tab").forEach((t) => t.classList.remove("nav__tab--active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("tab--active"));
    document.querySelector(`[data-tab="${tabId}"]`).classList.add("nav__tab--active");
    document.getElementById(`tab-${tabId}`).classList.add("tab--active");
    state.activeTab = tabId;
    if (tabId === "books") loadBooks();
    else if (tabId === "authors") loadAuthors();
    else loadOrders();
}

// ---------------------------------------------------------------------------
// AUTHORS
// ---------------------------------------------------------------------------

async function loadAuthors(offset = state.authors.offset) {
    const container = document.getElementById("authors-table");
    container.innerHTML = '<p class="loading">Loading…</p>';
    try {
        const result = await authorsApi.list(offset, state.authors.limit);
        Object.assign(state.authors, { offset, total: result.total, items: result.items });
        renderAuthorsTable(result.items);
        renderPagination("authors-pagination", offset, state.authors.limit, result.total, loadAuthors);
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Failed to load authors: ${escapeHtml(err.message)}</p>`;
    }
}

function renderAuthorsTable(authors) {
    const container = document.getElementById("authors-table");
    if (!authors.length) {
        container.innerHTML = '<p class="empty-state">No authors yet. Click "+ Add Author" to get started.</p>';
        return;
    }
    const rows = authors.map((a) => `
        <tr>
            <td>${escapeHtml(a.name)}</td>
            <td>${escapeHtml(a.bio || "—")}</td>
            <td>${new Date(a.created_at).toLocaleDateString()}</td>
            <td><div class="actions">
                <button class="btn btn--edit"   onclick="editAuthor(${a.id})">Edit</button>
                <button class="btn btn--danger" onclick="deleteAuthor(${a.id}, '${escapeHtml(a.name)}')">Delete</button>
            </div></td>
        </tr>`).join("");
    container.innerHTML = `
        <table>
            <thead><tr><th>Name</th><th>Bio</th><th>Created</th><th>Actions</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

function openAddAuthorModal() {
    openModal("Add Author", `
        <form id="author-form">
            <div class="form-group">
                <label>Name *</label>
                <input name="name" type="text" required placeholder="Author name" />
            </div>
            <div class="form-group">
                <label>Bio</label>
                <textarea name="bio" placeholder="Short biography"></textarea>
            </div>
        </form>`, async () => {
        await authorsApi.create(getFormData("author-form"));
        showToast("Author created successfully");
        loadAuthors(0);
    });
}

async function editAuthor(id) {
    try {
        const a = await authorsApi.get(id);
        openModal("Edit Author", `
            <form id="author-form">
                <div class="form-group">
                    <label>Name *</label>
                    <input name="name" type="text" required value="${escapeHtml(a.name)}" />
                </div>
                <div class="form-group">
                    <label>Bio</label>
                    <textarea name="bio">${escapeHtml(a.bio || "")}</textarea>
                </div>
            </form>`, async () => {
            await authorsApi.update(id, getFormData("author-form"));
            showToast("Author updated successfully");
            loadAuthors(state.authors.offset);
        });
    } catch (err) {
        showToast(`Failed to load author: ${err.message}`, "error");
    }
}

async function deleteAuthor(id, name) {
    if (!confirm(`Delete author "${name}"? This cannot be undone.`)) return;
    try {
        await authorsApi.delete(id);
        showToast("Author deleted");
        loadAuthors(0);
    } catch (err) {
        showToast(`Failed to delete: ${err.message}`, "error");
    }
}

// ---------------------------------------------------------------------------
// BOOKS
// ---------------------------------------------------------------------------

async function loadBooks(offset = state.books.offset) {
    const container = document.getElementById("books-table");
    container.innerHTML = '<p class="loading">Loading…</p>';
    try {
        const result = await booksApi.list(offset, state.books.limit);
        Object.assign(state.books, { offset, total: result.total, items: result.items });
        renderBooksTable(result.items);
        renderPagination("books-pagination", offset, state.books.limit, result.total, loadBooks);
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Failed to load books: ${escapeHtml(err.message)}</p>`;
    }
}

function renderBooksTable(books) {
    const container = document.getElementById("books-table");
    if (!books.length) {
        container.innerHTML = '<p class="empty-state">No books yet. Click "+ Add Book" to get started.</p>';
        return;
    }
    const rows = books.map((b) => `
        <tr>
            <td>${escapeHtml(b.title)}</td>
            <td><code>${escapeHtml(b.isbn)}</code></td>
            <td>$${parseFloat(b.price).toFixed(2)}</td>
            <td>${b.stock_quantity}</td>
            <td>${escapeHtml(b.author?.name || "Unknown")}</td>
            <td><div class="actions">
                <button class="btn btn--edit"   onclick="editBook(${b.id})">Edit</button>
                <button class="btn btn--danger" onclick="deleteBook(${b.id}, '${escapeHtml(b.title)}')">Delete</button>
            </div></td>
        </tr>`).join("");
    container.innerHTML = `
        <table>
            <thead><tr><th>Title</th><th>ISBN</th><th>Price</th><th>Stock</th><th>Author</th><th>Actions</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

async function buildAuthorOptions(selectedId = null) {
    try {
        const result = await authorsApi.list(0, 100);
        return result.items
            .map((a) => `<option value="${a.id}" ${a.id === selectedId ? "selected" : ""}>${escapeHtml(a.name)}</option>`)
            .join("");
    } catch (_) {
        return "";
    }
}

async function openAddBookModal() {
    const authorOptions = await buildAuthorOptions();
    openModal("Add Book", `
        <form id="book-form">
            <div class="form-group">
                <label>Title *</label>
                <input name="title" type="text" required placeholder="Book title" />
            </div>
            <div class="form-group">
                <label>ISBN *</label>
                <input name="isbn" type="text" required placeholder="10- or 13-digit ISBN" minlength="10" maxlength="13" />
            </div>
            <div class="form-group">
                <label>Price *</label>
                <input name="price" type="number" required step="0.01" min="0.01" placeholder="9.99" />
            </div>
            <div class="form-group">
                <label>Stock Quantity</label>
                <input name="stock_quantity" type="number" min="0" value="0" />
            </div>
            <div class="form-group">
                <label>Author *</label>
                <select name="author_id" required>
                    <option value="">Select an author</option>
                    ${authorOptions}
                </select>
            </div>
        </form>`, async () => {
        const data = getFormData("book-form");
        data.stock_quantity = Number(data.stock_quantity ?? 0);
        data.author_id = Number(data.author_id);
        await booksApi.create(data);
        showToast("Book created successfully");
        loadBooks(0);
    });
}

async function editBook(id) {
    try {
        const book = await booksApi.get(id);
        const opts = await buildAuthorOptions(book.author_id);
        openModal("Edit Book", `
            <form id="book-form">
                <div class="form-group">
                    <label>Title *</label>
                    <input name="title" type="text" required value="${escapeHtml(book.title)}" />
                </div>
                <div class="form-group">
                    <label>ISBN *</label>
                    <input name="isbn" type="text" required value="${escapeHtml(book.isbn)}" minlength="10" maxlength="13" />
                </div>
                <div class="form-group">
                    <label>Price *</label>
                    <input name="price" type="number" required step="0.01" min="0.01" value="${book.price}" />
                </div>
                <div class="form-group">
                    <label>Stock Quantity</label>
                    <input name="stock_quantity" type="number" min="0" value="${book.stock_quantity}" />
                </div>
                <div class="form-group">
                    <label>Author *</label>
                    <select name="author_id" required>
                        ${opts}
                    </select>
                </div>
            </form>`, async () => {
            const data = getFormData("book-form");
            data.stock_quantity = Number(data.stock_quantity);
            data.author_id = Number(data.author_id);
            await booksApi.update(id, data);
            showToast("Book updated successfully");
            loadBooks(state.books.offset);
        });
    } catch (err) {
        showToast(`Failed to load book: ${err.message}`, "error");
    }
}

async function deleteBook(id, title) {
    if (!confirm(`Delete book "${title}"? This cannot be undone.`)) return;
    try {
        await booksApi.delete(id);
        showToast("Book deleted");
        loadBooks(0);
    } catch (err) {
        showToast(`Failed to delete: ${err.message}`, "error");
    }
}

// ---------------------------------------------------------------------------
// ORDERS
// ---------------------------------------------------------------------------

async function loadOrders(offset = state.orders.offset) {
    const container = document.getElementById("orders-table");
    container.innerHTML = '<p class="loading">Loading…</p>';
    try {
        const result = await ordersApi.list(offset, state.orders.limit);
        Object.assign(state.orders, { offset, total: result.total, items: result.items });
        renderOrdersTable(result.items);
        renderPagination("orders-pagination", offset, state.orders.limit, result.total, loadOrders);
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Failed to load orders: ${escapeHtml(err.message)}</p>`;
    }
}

function renderOrdersTable(orders) {
    const container = document.getElementById("orders-table");
    if (!orders.length) {
        container.innerHTML = '<p class="empty-state">No orders yet. Click "+ Add Order" to create one.</p>';
        return;
    }
    const rows = orders.map((o) => `
        <tr>
            <td>#${o.id}</td>
            <td>${escapeHtml(o.customer_name)}</td>
            <td>${escapeHtml(o.customer_email)}</td>
            <td><span class="badge badge--${o.status}">${o.status}</span></td>
            <td>$${parseFloat(o.total_amount).toFixed(2)}</td>
            <td>${new Date(o.created_at).toLocaleDateString()}</td>
            <td><div class="actions">
                <button class="btn btn--status" onclick="openUpdateStatusModal(${o.id}, '${o.status}')">Status</button>
            </div></td>
        </tr>`).join("");
    container.innerHTML = `
        <table>
            <thead><tr><th>#</th><th>Customer</th><th>Email</th><th>Status</th><th>Total</th><th>Date</th><th>Actions</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

async function openAddOrderModal() {
    let bookOptions = "";
    try {
        const result = await booksApi.list(0, 100);
        bookOptions = result.items
            .map((b) => `<option value="${b.id}">${escapeHtml(b.title)} ($${parseFloat(b.price).toFixed(2)})</option>`)
            .join("");
    } catch (_) {}

    openModal("Create Order", `
        <form id="order-form">
            <div class="form-group">
                <label>Customer Name *</label>
                <input name="customer_name" type="text" required placeholder="Jane Doe" />
            </div>
            <div class="form-group">
                <label>Customer Email *</label>
                <input name="customer_email" type="email" required placeholder="jane@example.com" />
            </div>
            <div class="form-group">
                <label>Order Items *</label>
                <div class="order-items" id="order-items">
                    <div class="order-item">
                        <select class="item-book" required>
                            <option value="">Select book</option>
                            ${bookOptions}
                        </select>
                        <input class="item-qty" type="number" min="1" value="1" />
                        <button type="button" class="btn btn--danger" onclick="removeOrderItem(this)">✕</button>
                    </div>
                </div>
                <button type="button" class="btn btn--secondary" style="margin-top:0.5rem"
                    data-book-options="${escapeHtml(bookOptions)}"
                    onclick="addOrderItem(this)">+ Add Item</button>
            </div>
        </form>`, async () => {
        const formData = getFormData("order-form");
        const items = Array.from(document.querySelectorAll(".order-item"))
            .map((el) => ({
                book_id: Number(el.querySelector(".item-book").value),
                quantity: Number(el.querySelector(".item-qty").value),
            }))
            .filter((item) => item.book_id > 0);
        if (!items.length) throw new ApiError(400, "At least one book item is required");
        await ordersApi.create({ ...formData, items });
        showToast("Order created successfully");
        loadOrders(0);
    });
}

function addOrderItem(btn) {
    const bookOptions = btn.dataset.bookOptions || "";
    const div = document.createElement("div");
    div.className = "order-item";
    div.innerHTML = `
        <select class="item-book" required>
            <option value="">Select book</option>
            ${bookOptions}
        </select>
        <input class="item-qty" type="number" min="1" value="1" />
        <button type="button" class="btn btn--danger" onclick="removeOrderItem(this)">✕</button>`;
    document.getElementById("order-items").appendChild(div);
}

function removeOrderItem(btn) {
    const items = document.querySelectorAll(".order-item");
    if (items.length > 1) btn.closest(".order-item").remove();
}

function openUpdateStatusModal(id, currentStatus) {
    const opts = ORDER_STATUSES
        .map((s) => `<option value="${s}" ${s === currentStatus ? "selected" : ""}>${s}</option>`)
        .join("");
    openModal("Update Order Status", `
        <form id="status-form">
            <div class="form-group">
                <label>New Status</label>
                <select name="status">${opts}</select>
            </div>
        </form>`, async () => {
        const { status } = getFormData("status-form");
        await ordersApi.updateStatus(id, status);
        showToast("Order status updated");
        loadOrders(state.orders.offset);
    });
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    // Tab switching
    document.querySelectorAll(".nav__tab").forEach((tab) => {
        tab.addEventListener("click", () => switchTab(tab.dataset.tab));
    });

    // Modal controls
    document.getElementById("modal-close").addEventListener("click", closeModal);
    document.getElementById("modal-cancel").addEventListener("click", closeModal);
    document.getElementById("modal-overlay").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeModal();
    });

    document.getElementById("modal-submit").addEventListener("click", async () => {
        if (!modalSubmitHandler) return;
        const submitBtn = document.getElementById("modal-submit");
        submitBtn.disabled = true;
        try {
            await modalSubmitHandler();
            closeModal();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            submitBtn.disabled = false;
        }
    });

    // Section action buttons
    document.getElementById("btn-add-book").addEventListener("click", openAddBookModal);
    document.getElementById("btn-add-author").addEventListener("click", openAddAuthorModal);
    document.getElementById("btn-add-order").addEventListener("click", openAddOrderModal);

    // Initial data load
    loadBooks();
});
