import os
import tempfile
import unittest
from datetime import date

from app import app
import app as library_app


class LibraryBookTrackerTests(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(delete=False)
        self.database.close()
        self.original_database = library_app.DATABASE
        library_app.DATABASE = self.database.name
        library_app.init_db()
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def tearDown(self):
        library_app.DATABASE = self.original_database
        os.unlink(self.database.name)

    def add_book(self, title="Clean Code"):
        return self.client.post(
            "/add",
            data={
                "title": title,
                "author": "Robert Martin",
                "student_name": "Alex",
                "student_id": "S001",
            },
            follow_redirects=True,
        )

    def test_add_search_return_and_export(self):
        response = self.add_book()
        self.assertIn(b"Clean Code", response.data)

        response = self.client.get("/?search=Clean&status=Issued")
        self.assertIn(b"Clean Code", response.data)

        response = self.client.post("/return/1", follow_redirects=True)
        self.assertIn(b"Returned", response.data)
        self.assertIn(date.today().isoformat().encode(), response.data)

        response = self.client.get("/export")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Clean Code", response.data)
        self.assertIn(b"Returned", response.data)

    def test_duplicate_active_issue_is_rejected(self):
        self.add_book()
        response = self.add_book()
        self.assertIn(b"already has this book issued", response.data)

    def test_edit_and_delete(self):
        self.add_book()
        response = self.client.get("/?edit=1")
        self.assertIn(b"Edit Book #1", response.data)

        response = self.client.post(
            "/edit/1",
            data={
                "title": "Refactoring",
                "author": "Martin Fowler",
                "student_name": "Alex",
                "student_id": "S001",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Refactoring", response.data)
        response = self.client.post("/delete/1", follow_redirects=True)
        self.assertIn(b"No books found", response.data)


if __name__ == "__main__":
    unittest.main()
