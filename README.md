# Reading Room — Library Book Management System

A CRUD mini web application built for the SOP.

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript (Fetch API) |
| Backend | Django 5 (JSON views, no extra packages) |
| Database | SQLite 3 |

---

## 1. Project structure

```
library-system/
├── manage.py
├── requirements.txt
├── db.sqlite3               (created on first migrate)
├── library/                 project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── catalog/                 the app
│   ├── models.py            Book model
│   ├── views.py             JSON API + page view
│   ├── urls.py              API routes
│   ├── admin.py
│   ├── tests.py             8 unit tests
│   └── migrations/
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## 2. Run it in VS Code

Open the `library-system` folder in VS Code, then in the integrated terminal:

```bash
# 1. virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 2. install Django
pip install -r requirements.txt

# 3. create the SQLite tables
python manage.py makemigrations catalog
python manage.py migrate

# 4. (optional) admin login for /admin/
python manage.py createsuperuser

# 5. start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

Recommended VS Code extensions: *Python* (Microsoft) and *SQLite Viewer* (to open `db.sqlite3` for your screenshots).

---

## 3. Database design

Table `catalog_book`

| Column | Type | Constraint |
|---|---|---|
| id | integer | primary key, auto |
| title | varchar(200) | required |
| author | varchar(120) | required |
| isbn | varchar(20) | **unique**, 10 or 13 digits |
| category | varchar(20) | one of 6 choices |
| published_year | integer | 1450–2100 |
| shelf | varchar(20) | optional |
| total_copies | integer | ≥ 1 |
| available_copies | integer | ≤ total_copies |
| created_at | datetime | auto on insert |
| updated_at | datetime | auto on update |

---

## 4. API endpoints

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/books/` | List (supports `?search=`, `?category=`, `?status=`, `?sort=`) |
| POST | `/api/books/` | **Create** a book |
| GET | `/api/books/<id>/` | **Read** one book |
| PUT | `/api/books/<id>/` | **Update** a book |
| DELETE | `/api/books/<id>/` | **Delete** a book |
| POST | `/api/books/<id>/issue/` | Issue one copy |
| POST | `/api/books/<id>/return/` | Return one copy |
| GET | `/api/stats/` | Totals for the header counters |

All responses are JSON. Validation failures return HTTP 400 with
`{"errors": {"field": "message"}}`, which the frontend paints under the matching input.

---

## 5. Features covered

- **Create** — form with client-side `required` attributes and full server-side validation.
- **Read** — live list with search (title / author / ISBN), category filter, availability filter and four sort orders.
- **Update** — Edit loads the record back into the form; the total copies can't be dropped below the number currently issued.
- **Delete** — with a confirmation prompt.
- **Extra logic** — issue and return copies; the coloured left edge of each row shows availability (green on shelf, brass partly issued, red all out).
- **Error handling** — duplicate ISBN, malformed ISBN, out-of-range year, issuing with zero copies left, acting on a deleted record.
- **Security** — CSRF token sent with every write request; all user text escaped before insertion into the DOM.
- **Responsive** — three-breakpoint layout, visible keyboard focus, reduced-motion respected.

---

## 6. Testing

```bash
python manage.py test
```

Eight tests in `catalog/tests.py` cover listing, creation, ISBN validation,
search, update, issue/return, the zero-copies guard, and deletion.

For the manual test table in your report, here are good cases to record:

| # | Test case | Input | Expected |
|---|---|---|---|
| 1 | Add valid book | Complete form | Row appears, counters increase |
| 2 | Duplicate ISBN | Existing ISBN | Error under the ISBN field |
| 3 | Short ISBN | `123` | "ISBN must be 10 or 13 digits" |
| 4 | Invalid year | `3000` | "Enter a year between 1450 and 2100" |
| 5 | Search | Author name | Only matching rows shown |
| 6 | Edit | Change title, save | Row updates, no duplicate created |
| 7 | Issue all copies | Click Issue n times | Issue button disables, edge turns red |
| 8 | Return | Click Return | Available count increases |
| 9 | Delete | Confirm prompt | Row disappears, counters drop |

---

## 7. Sample data for the demo

| Title | Author | ISBN | Category | Year | Copies |
|---|---|---|---|---|---|
| The Pragmatic Programmer | Andrew Hunt | 9780201616224 | Technology | 1999 | 3 |
| Sapiens | Yuval Noah Harari | 9780099590088 | History | 2011 | 2 |
| A Brief History of Time | Stephen Hawking | 9780553380163 | Science | 1988 | 4 |
| Wings of Fire | A. P. J. Abdul Kalam | 9788173711466 | Biography | 1999 | 5 |
| The Namesake | Jhumpa Lahiri | 9780618485222 | Fiction | 2003 | 2 |
