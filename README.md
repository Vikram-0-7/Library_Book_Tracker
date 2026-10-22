# 📚 Library Book Tracker

A beginner-friendly Flask web application that helps a college library track issued and returned books. Data is stored in **SQLite** and the app is ready to be containerised with **Docker**.

---

## Features

- **Add** a book with title, author, student name, and student ID.
- **View** all books in a clean HTML table.
- **Search** books by title, author, or student name.
- **Track status** – each book is marked as *Issued* or *Returned*.
- **Return** – mark an issued book as returned with one click.
- **Delete** – remove a book from the tracker.
- **Persistent storage** – SQLite database stored in a `data/` directory.
- **Input validation** and parameterized SQL queries to prevent SQL injection.

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

## Docker (coming soon)

A `Dockerfile` will be added to containerise the application. The `data/` directory can be mounted as a Docker volume so the SQLite database persists across container restarts.

---

## License

This project is for educational purposes.
