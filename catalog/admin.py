from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "published_year",
                    "available_copies", "total_copies")
    list_filter = ("category",)
    search_fields = ("title", "author", "isbn")
