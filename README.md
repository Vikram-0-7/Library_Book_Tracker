# 📚 Library Book Tracker

A beginner-friendly Flask web application that helps a college library track issued and returned books. Data is stored in **SQLite** and the app is ready to be containerised with **Docker**.

---

## Features

- **Add** a book with title, author, student name, and student ID.
- **View** all books in a clean HTML table.
- **Search** books by title, author, or student name.
- **Track status** – each book is marked as *Issued* or *Returned*.
- **Return** – mark an issued book as returned with one click.
- **Edit** – correct existing book and borrower details.
- **Filter** – filter records by issued, returned, or overdue status.
- **Return dates** – record and display when a book was returned.
- **CSV export** – download records for reporting or backup.
- **Pagination** – keep larger record sets easy to navigate.
- **Delete** – remove a book from the tracker.
- **Persistent storage** – SQLite database stored in a `data/` directory.
- **Input validation**, duplicate issue prevention, and parameterized SQL queries.

---

## Project Structure

```
library-book-tracker/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # HTML template
├── static/
│   └── style.css       # Stylesheet
├── data/               # SQLite database (auto-created, git-ignored)
├── tests/              # Automated application tests
├── Dockerfile          # Container image definition
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Python 3.12** (or any recent 3.x version)
- **pip** (comes with Python)

---

## Local Setup

### 1. Create and activate a virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

The app starts on **http://localhost:5000** by default.

### 4. Change the port (optional)

Set the `FLASK_PORT` environment variable before running:

```bash
# Windows (PowerShell)
$env:FLASK_PORT = "8080"
python app.py

# macOS / Linux
FLASK_PORT=8080 python app.py
```

---

### 5. Configure the application (optional)

For deployments, set a unique secret key and keep debug mode disabled:

```powershell
$env:FLASK_SECRET_KEY = "replace-with-a-long-random-value"
$env:FLASK_DEBUG = "0"
```

### 6. Run tests

```bash
python -m unittest discover -s tests -v
```

## Docker

Build and run the application with persistent SQLite storage:

```bash
docker build -t library-book-tracker .
docker run --rm -p 5000:5000 -v library-data:/app/data library-book-tracker
```

The application is available at **http://localhost:5000**.

---

## License

This project is for educational purposes.
