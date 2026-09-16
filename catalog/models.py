from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Book(models.Model):
    """One title held by the library, with a count of physical copies."""

    CATEGORY_CHOICES = [
        ("fiction", "Fiction"),
        ("science", "Science"),
        ("technology", "Technology"),
        ("history", "History"),
        ("biography", "Biography"),
        ("reference", "Reference"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="fiction"
    )
    published_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1450), MaxValueValidator(2100)]
    )
    shelf = models.CharField(max_length=20, blank=True)
    total_copies = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} — {self.author}"

    @property
    def issued_copies(self):
        return self.total_copies - self.available_copies

    @property
    def status(self):
        if self.available_copies == 0:
            return "out"
        if self.available_copies < self.total_copies:
            return "partial"
        return "in"

    def to_dict(self):
        """Shape sent to the browser. Keep this the single source of truth."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "category_label": self.get_category_display(),
            "published_year": self.published_year,
            "shelf": self.shelf,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "issued_copies": self.issued_copies,
            "status": self.status,
            "updated_at": self.updated_at.strftime("%d %b %Y, %I:%M %p"),
        }
