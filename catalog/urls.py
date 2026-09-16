from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/books/", views.book_collection, name="book-collection"),
    path("api/books/<int:pk>/", views.book_detail, name="book-detail"),
    path("api/books/<int:pk>/issue/", views.book_issue, name="book-issue"),
    path("api/books/<int:pk>/return/", views.book_return, name="book-return"),
    path("api/stats/", views.stats, name="stats"),
]
