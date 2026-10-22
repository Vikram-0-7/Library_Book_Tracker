"""
Library Book Tracker - A Flask web application for tracking college library books.

Features:
    - Add books with title, author, student name, and student ID.
    - View all books in a table.
    - Search books by title, author, or student name.
    - Mark issued books as returned.
    - Delete books from the tracker.
    - Data is stored in SQLite for persistence.
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "library-secret-key"  # Needed for flash messages

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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            author      TEXT    NOT NULL,
            student_name TEXT   NOT NULL,
            student_id  TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Issued'
        )
        """
    )
    conn.commit()
    conn.close()


# Create the table when the app starts.
init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Home page – show the search form and all books (or filtered results)."""
    search_query = request.args.get("search", "").strip()
    conn = get_db()

    if search_query:
        # Use parameterized queries to prevent SQL injection.
        like_pattern = f"%{search_query}%"
        books = conn.execute(
            """
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR student_name LIKE ?
            ORDER BY id DESC
            """,
            (like_pattern, like_pattern, like_pattern),
        ).fetchall()
    else:
        books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()

    conn.close()
    return render_template("index.html", books=books, search_query=search_query)


@app.route("/add", methods=["POST"])
def add_book():
    """Add a new book to the tracker."""
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    student_name = request.form.get("student_name", "").strip()
    student_id = request.form.get("student_id", "").strip()

    # --- Input validation ---
    if not all([title, author, student_name, student_id]):
        flash("All fields are required.", "error")
        return redirect(url_for("index"))

    conn = get_db()
    conn.execute(
        "INSERT INTO books (title, author, student_name, student_id) VALUES (?, ?, ?, ?)",
        (title, author, student_name, student_id),
    )
    conn.commit()
    conn.close()

    flash(f'Book "{title}" added successfully!', "success")
    return redirect(url_for("index"))


@app.route("/return/<int:book_id>", methods=["POST"])
def return_book(book_id):
    """Mark an issued book as returned."""
    conn = get_db()
    conn.execute("UPDATE books SET status = 'Returned' WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    flash("Book marked as returned.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    """Delete a book from the tracker."""
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    flash("Book deleted.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
