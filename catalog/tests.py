"""Unit tests for the SOP's testing section. Run: python manage.py test"""
import json

from django.test import TestCase
from django.urls import reverse

from .models import Book


class BookApiTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt",
            isbn="9780201616224",
            category="technology",
            published_year=1999,
            total_copies=3,
            available_copies=3,
        )

    def post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload),
                                content_type="application/json")

    def test_list_returns_seeded_book(self):
        res = self.client.get(reverse("book-collection"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["books"]), 1)

    def test_create_valid_book(self):
        res = self.post_json(reverse("book-collection"), {
            "title": "Clean Code", "author": "Robert C. Martin",
            "isbn": "9780132350884", "category": "technology",
            "published_year": 2008, "total_copies": 2,
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_rejects_bad_isbn(self):
        res = self.post_json(reverse("book-collection"), {
            "title": "Bad Book", "author": "Nobody", "isbn": "123",
            "category": "fiction", "published_year": 2020, "total_copies": 1,
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("isbn", res.json()["errors"])

    def test_search_filters_by_author(self):
        res = self.client.get(reverse("book-collection"), {"search": "Hunt"})
        self.assertEqual(len(res.json()["books"]), 1)
        res = self.client.get(reverse("book-collection"), {"search": "zzzz"})
        self.assertEqual(len(res.json()["books"]), 0)

    def test_update_book(self):
        url = reverse("book-detail", args=[self.book.id])
        res = self.client.put(url, data=json.dumps({
            "title": "The Pragmatic Programmer, 2nd Ed",
            "author": "Andrew Hunt", "isbn": "9780201616224",
            "category": "technology", "published_year": 2019,
            "total_copies": 3,
        }), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.published_year, 2019)

    def test_issue_then_return(self):
        issue_url = reverse("book-issue", args=[self.book.id])
        self.client.post(issue_url)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

        self.client.post(reverse("book-return", args=[self.book.id]))
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 3)

    def test_cannot_issue_when_none_left(self):
        self.book.available_copies = 0
        self.book.save()
        res = self.client.post(reverse("book-issue", args=[self.book.id]))
        self.assertEqual(res.status_code, 400)

    def test_delete_book(self):
        res = self.client.delete(reverse("book-detail", args=[self.book.id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)
