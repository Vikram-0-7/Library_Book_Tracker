"""
Library Book Tracker - A Flask web application for tracking college library books.

Features:
    - Add books with title, author, student name, and student ID.
    - View all books in a table.
    - Search books by title, author, or student name.
    - Track due dates and highlight overdue books.
    - Mark issued books as returned.
    - Delete books from the tracker.
    - Data is stored in SQLite for persistence.
"""

import os
import sqlite3
import csv
import io
from datetime import date, timedelta
from flask import Flask, Response, render_template, request, redirect, url_for, flash

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development-only-change-me")

# Store the database in a "data" directory so it can be mounted as a Docker volume.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE = os.path.join(DATA_DIR, "library.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    """Open a new SQLite connection and return it."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Create the books table if it does not already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            author       TEXT    NOT NULL,
            student_name TEXT    NOT NULL,
            student_id   TEXT    NOT NULL,
            status       TEXT    NOT NULL DEFAULT 'Issued',
            issued_date  TEXT,
            due_date     TEXT
        )
        """
    )

    # If the table already existed without the new columns, add them.
    for column in ("issued_date TEXT", "due_date TEXT", "returned_date TEXT"):
        try:
            conn.execute(f"ALTER TABLE books ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    conn.commit()
    conn.close()


# Create the table when the app starts.
init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Home page – show dashboard stats, the search form, and all books."""
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All")
    if status_filter not in {"All", "Issued", "Returned", "Overdue"}:
        status_filter = "All"
    edit_id = request.args.get("edit", type=int)
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = 10
    today = date.today().isoformat()
    conn = get_db()

    conditions = []
    parameters = []
    if search_query:
        # Use parameterized queries to prevent SQL injection.
        like_pattern = f"%{search_query}%"
        conditions.append("(title LIKE ? OR author LIKE ? OR student_name LIKE ? OR student_id LIKE ?)")
        parameters.extend([like_pattern] * 4)
    if status_filter == "Issued":
        conditions.append("status = 'Issued'")
    elif status_filter == "Returned":
        conditions.append("status = 'Returned'")
    elif status_filter == "Overdue":
        conditions.append("status = 'Issued' AND due_date < ?")
        parameters.append(today)

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    total_matching = conn.execute(
        f"SELECT COUNT(*) FROM books{where_clause}", parameters
    ).fetchone()[0]
    total_pages = max((total_matching + per_page - 1) // per_page, 1)
    page = min(page, total_pages)
    books = conn.execute(
        f"SELECT * FROM books{where_clause} ORDER BY id DESC LIMIT ? OFFSET ?",
        parameters + [per_page, (page - 1) * per_page],
    ).fetchall()

    # Dashboard statistics
    stats = conn.execute(
        """
        SELECT
            COUNT(*)                                               AS total,
            SUM(CASE WHEN status = 'Issued'   THEN 1 ELSE 0 END)  AS issued,
            SUM(CASE WHEN status = 'Returned'  THEN 1 ELSE 0 END) AS returned,
            SUM(CASE WHEN status = 'Issued' AND due_date < ? THEN 1 ELSE 0 END) AS overdue
        FROM books
        """,
        (today,),
    ).fetchone()

    edit_book = None
    if edit_id is not None:
        edit_book = conn.execute("SELECT * FROM books WHERE id = ?", (edit_id,)).fetchone()
    conn.close()
    return render_template(
        "index.html", books=books, search_query=search_query, status_filter=status_filter,
        stats=stats, today=today, edit_book=edit_book, page=page, total_pages=total_pages
    )


def read_book_fields():
    """Read and validate the fields shared by add and edit operations."""
    fields = {
        name: request.form.get(name, "").strip()
        for name in ("title", "author", "student_name", "student_id")
    }
    if not all(fields.values()):
        return None, "All fields are required."
    if any(len(value) > 120 for value in fields.values()):
        return None, "Each field must be 120 characters or fewer."
    return fields, None


@app.route("/add", methods=["POST"])
def add_book():
    """Add a new book to the tracker."""
    fields, error = read_book_fields()
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    conn = get_db()
    duplicate = conn.execute(
        "SELECT 1 FROM books WHERE title = ? AND student_id = ? AND status = 'Issued'",
        (fields["title"], fields["student_id"]),
    ).fetchone()
    if duplicate:
        conn.close()
        flash("This student already has this book issued.", "error")
        return redirect(url_for("index"))

    today = date.today()
    due = today + timedelta(days=14)
    conn.execute(
        """INSERT INTO books (title, author, student_name, student_id, issued_date, due_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (fields["title"], fields["author"], fields["student_name"], fields["student_id"],
         today.isoformat(), due.isoformat()),
    )
    conn.commit()
    conn.close()

    flash(f'Book "{fields["title"]}" added successfully!', "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:book_id>", methods=["POST"])
def edit_book(book_id):
    """Update the details of an existing book record."""
    fields, error = read_book_fields()
    if error:
        flash(error, "error")
        return redirect(url_for("index", edit=book_id))

    conn = get_db()
    duplicate = conn.execute(
        """SELECT 1 FROM books
           WHERE title = ? AND student_id = ? AND status = 'Issued' AND id != ?""",
        (fields["title"], fields["student_id"], book_id),
    ).fetchone()
    if duplicate:
        conn.close()
        flash("This student already has this book issued.", "error")
        return redirect(url_for("index", edit=book_id))

    updated = conn.execute(
        """UPDATE books SET title = ?, author = ?, student_name = ?, student_id = ?
           WHERE id = ?""",
        (fields["title"], fields["author"], fields["student_name"], fields["student_id"], book_id),
    )
    conn.commit()
    conn.close()
    if updated.rowcount == 0:
        flash("Book record not found.", "error")
    else:
        flash("Book details updated.", "success")
    return redirect(url_for("index"))


@app.route("/return/<int:book_id>", methods=["POST"])
def return_book(book_id):
    """Mark an issued book as returned."""
    conn = get_db()
    updated = conn.execute(
        "UPDATE books SET status = 'Returned', returned_date = ? WHERE id = ? AND status = 'Issued'",
        (date.today().isoformat(), book_id),
    )
    conn.commit()
    conn.close()

    flash("Book marked as returned." if updated.rowcount else "Book is already returned or was not found.",
          "success" if updated.rowcount else "error")
    return redirect(url_for("index"))


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    """Delete a book from the tracker."""
    conn = get_db()
    deleted = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    flash("Book deleted." if deleted.rowcount else "Book record not found.",
          "success" if deleted.rowcount else "error")
    return redirect(url_for("index"))


@app.route("/export")
def export_books():
    """Download the current library records as a CSV file."""
    conn = get_db()
    books = conn.execute(
        """SELECT id, title, author, student_name, student_id, status,
                  issued_date, due_date, returned_date
           FROM books ORDER BY id DESC"""
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Author", "Student Name", "Student ID", "Status",
                    "Issued Date", "Due Date", "Returned Date"])
    writer.writerows(tuple(book) for book in books)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=library-books.csv"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
