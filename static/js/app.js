/* ====================================================================
   Reading Room — frontend logic
   Talks to the Django JSON API at /api/books/
   ==================================================================== */

const CSRF = document.querySelector('meta[name="csrf-token"]').content;

const form       = document.getElementById('book-form');
const idField    = document.getElementById('book-id');
const submitBtn  = document.getElementById('submit-btn');
const cancelBtn  = document.getElementById('cancel-btn');
const formHeading= document.getElementById('form-heading');
const list       = document.getElementById('book-list');
const emptyNote  = document.getElementById('empty');
const toast      = document.getElementById('toast');

const search       = document.getElementById('search');
const filterCat    = document.getElementById('filter-category');
const filterStatus = document.getElementById('filter-status');
const sortBy       = document.getElementById('sort');

/* ------------------------------------------------------------ helpers */

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

let toastTimer;
function say(message, kind = 'ok') {
  toast.textContent = message;
  toast.dataset.kind = kind;
  toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}

function clearErrors() {
  document.querySelectorAll('.field__error').forEach((p) => (p.textContent = ''));
  document.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
}

function showErrors(errors) {
  clearErrors();
  Object.entries(errors || {}).forEach(([field, message]) => {
    const slot = document.querySelector(`[data-error="${field}"]`);
    if (slot) slot.textContent = message;
    const input = document.getElementById(field);
    if (input) input.classList.add('is-invalid');
  });
}

/* ------------------------------------------------------ read the list */

function buildQuery() {
  const params = new URLSearchParams();
  if (search.value.trim()) params.set('search', search.value.trim());
  if (filterCat.value) params.set('category', filterCat.value);
  if (filterStatus.value) params.set('status', filterStatus.value);
  params.set('sort', sortBy.value);
  return params.toString();
}

async function loadBooks() {
  const { ok, data } = await api(`/api/books/?${buildQuery()}`);
  if (!ok) { say('Could not load the catalogue.', 'error'); return; }
  render(data.books);
  loadStats();
}

async function loadStats() {
  const { ok, data } = await api('/api/stats/');
  if (!ok) return;
  Object.entries(data).forEach(([key, value]) => {
    const cell = document.querySelector(`[data-tally="${key}"]`);
    if (cell) cell.textContent = value;
  });
}

function render(books) {
  list.innerHTML = '';

  if (!books.length) {
    emptyNote.hidden = false;
    emptyNote.textContent = search.value || filterCat.value || filterStatus.value
      ? 'No book matches these filters. Clear the search to see everything.'
      : 'The catalogue is empty. Add your first book using the form.';
    return;
  }
  emptyNote.hidden = true;

  books.forEach((book) => {
    const li = document.createElement('li');
    li.className = 'book';
    li.dataset.status = book.status;
    li.innerHTML = `
      <div>
        <h3 class="book__title">${escapeHtml(book.title)}</h3>
        <p class="book__byline">${escapeHtml(book.author)}, ${book.published_year}</p>
        <p class="book__meta">
          <span>${escapeHtml(book.category_label)}</span>
          <span>ISBN ${escapeHtml(book.isbn)}</span>
          ${book.shelf ? `<span>Shelf ${escapeHtml(book.shelf)}</span>` : ''}
          <span>Updated ${escapeHtml(book.updated_at)}</span>
        </p>
      </div>
      <p class="book__copies">
        <b>${book.available_copies}/${book.total_copies}</b>
        <span>on shelf</span>
      </p>
      <div class="book__actions">
        <button class="btn btn--small" data-act="issue"  data-id="${book.id}"
          ${book.available_copies === 0 ? 'disabled' : ''}>Issue</button>
        <button class="btn btn--small" data-act="return" data-id="${book.id}"
          ${book.issued_copies === 0 ? 'disabled' : ''}>Return</button>
        <button class="btn btn--small" data-act="edit"   data-id="${book.id}">Edit</button>
        <button class="btn btn--small btn--danger" data-act="delete" data-id="${book.id}">Delete</button>
      </div>`;
    list.appendChild(li);
  });
}

/* ------------------------------------------------------ create/update */

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearErrors();

  const payload = {
    title: document.getElementById('title').value,
    author: document.getElementById('author').value,
    isbn: document.getElementById('isbn').value,
    category: document.getElementById('category').value,
    published_year: document.getElementById('published_year').value,
    total_copies: document.getElementById('total_copies').value,
    shelf: document.getElementById('shelf').value,
  };

  const editingId = idField.value;
  const { ok, data } = await api(
    editingId ? `/api/books/${editingId}/` : '/api/books/',
    { method: editingId ? 'PUT' : 'POST', body: JSON.stringify(payload) }
  );

  if (!ok) { showErrors(data.errors); say('Fix the highlighted fields.', 'error'); return; }

  say(editingId ? 'Changes saved.' : `“${data.book.title}” added.`);
  resetForm();
  loadBooks();
});

function resetForm() {
  form.reset();
  idField.value = '';
  clearErrors();
  document.getElementById('total_copies').value = 1;
  formHeading.textContent = 'Add a book';
  submitBtn.textContent = 'Save book';
  cancelBtn.hidden = true;
}

cancelBtn.addEventListener('click', resetForm);

async function startEdit(id) {
  const { ok, data } = await api(`/api/books/${id}/`);
  if (!ok) { say('That book is no longer in the catalogue.', 'error'); return; }

  const book = data.book;
  idField.value = book.id;
  document.getElementById('title').value = book.title;
  document.getElementById('author').value = book.author;
  document.getElementById('isbn').value = book.isbn;
  document.getElementById('category').value = book.category;
  document.getElementById('published_year').value = book.published_year;
  document.getElementById('total_copies').value = book.total_copies;
  document.getElementById('shelf').value = book.shelf;

  clearErrors();
  formHeading.textContent = 'Edit book';
  submitBtn.textContent = 'Save changes';
  cancelBtn.hidden = false;
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ------------------------------------------------- row button actions */

list.addEventListener('click', async (event) => {
  const button = event.target.closest('button[data-act]');
  if (!button) return;

  const { act, id } = button.dataset;

  if (act === 'edit') return startEdit(id);

  if (act === 'delete') {
    if (!confirm('Remove this book from the catalogue?')) return;
    const { ok, data } = await api(`/api/books/${id}/`, { method: 'DELETE' });
    if (!ok) { say(data.errors?.__all__ || 'Delete failed.', 'error'); return; }
    if (idField.value === id) resetForm();
    say(`“${data.title}” removed.`);
    return loadBooks();
  }

  const { ok, data } = await api(`/api/books/${id}/${act}/`, { method: 'POST' });
  if (!ok) { say(data.errors?.__all__ || 'That action failed.', 'error'); return; }
  say(act === 'issue' ? 'Copy issued.' : 'Copy returned.');
  loadBooks();
});

/* ----------------------------------------------------------- filters */

let searchTimer;
search.addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadBooks, 250);
});

[filterCat, filterStatus, sortBy].forEach((el) => el.addEventListener('change', loadBooks));

loadBooks();
