import json

from django.db import IntegrityError
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import Book

VALID_CATEGORIES = {key for key, _ in Book.CATEGORY_CHOICES}


# ------------------------------------------------------------------ page
def home(request):
    """Serve the single page that the JavaScript talks to."""
    return render(request, "index.html", {"categories": Book.CATEGORY_CHOICES})


# ------------------------------------------------------------- validation
def read_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, "The request body wasn't valid JSON."


def clean_book_payload(data, instance=None):
    """Return (cleaned_dict, errors_dict). Server-side validation lives here."""
    errors = {}
    cleaned = {}

    title = str(data.get("title", "")).strip()
    if len(title) < 2:
        errors["title"] = "Enter a title of at least 2 characters."
    cleaned["title"] = title

    author = str(data.get("author", "")).strip()
    if len(author) < 2:
        errors["author"] = "Enter the author's name."
    cleaned["author"] = author

    isbn = str(data.get("isbn", "")).strip().replace("-", "").replace(" ", "")
    if not isbn.isdigit() or len(isbn) not in (10, 13):
        errors["isbn"] = "ISBN must be 10 or 13 digits."
    else:
        clash = Book.objects.filter(isbn=isbn)
        if instance:
            clash = clash.exclude(pk=instance.pk)
        if clash.exists():
            errors["isbn"] = "Another book already uses this ISBN."
    cleaned["isbn"] = isbn

    category = str(data.get("category", "")).strip()
    if category not in VALID_CATEGORIES:
        errors["category"] = "Choose a category from the list."
    cleaned["category"] = category

    try:
        year = int(data.get("published_year"))
        if not 1450 <= year <= 2100:
            raise ValueError
        cleaned["published_year"] = year
    except (TypeError, ValueError):
        errors["published_year"] = "Enter a year between 1450 and 2100."

    try:
        total = int(data.get("total_copies", 1))
        if total < 1:
            raise ValueError
        cleaned["total_copies"] = total
    except (TypeError, ValueError):
        errors["total_copies"] = "Enter at least 1 copy."

    cleaned["shelf"] = str(data.get("shelf", "")).strip()[:20]

    return cleaned, errors


# --------------------------------------------------------------- list/add
@require_http_methods(["GET", "POST"])
def book_collection(request):
    if request.method == "GET":
        books = Book.objects.all()

        search = request.GET.get("search", "").strip()
        if search:
            books = books.filter(
                Q(title__icontains=search)
                | Q(author__icontains=search)
                | Q(isbn__icontains=search)
            )

        category = request.GET.get("category", "").strip()
        if category in VALID_CATEGORIES:
            books = books.filter(category=category)

        status = request.GET.get("status", "").strip()
        if status == "available":
            books = books.filter(available_copies__gt=0)
        elif status == "out":
            books = books.filter(available_copies=0)

        sort = request.GET.get("sort", "title")
        if sort in {"title", "author", "published_year", "-updated_at"}:
            books = books.order_by(sort)

        return JsonResponse({"books": [b.to_dict() for b in books]})

    # POST — create
    data, parse_error = read_json(request)
    if parse_error:
        return JsonResponse({"errors": {"__all__": parse_error}}, status=400)

    cleaned, errors = clean_book_payload(data)
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    try:
        book = Book.objects.create(
            **cleaned, available_copies=cleaned["total_copies"]
        )
    except IntegrityError:
        return JsonResponse({"errors": {"isbn": "That ISBN is already saved."}}, status=400)

    return JsonResponse({"book": book.to_dict()}, status=201)


# ------------------------------------------------------ read/update/delete
@require_http_methods(["GET", "PUT", "DELETE"])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"errors": {"__all__": "That book is no longer in the catalogue."}}, status=404)

    if request.method == "GET":
        return JsonResponse({"book": book.to_dict()})

    if request.method == "DELETE":
        title = book.title
        book.delete()
        return JsonResponse({"deleted": pk, "title": title})

    # PUT — update
    data, parse_error = read_json(request)
    if parse_error:
        return JsonResponse({"errors": {"__all__": parse_error}}, status=400)

    cleaned, errors = clean_book_payload(data, instance=book)
    if not errors and cleaned["total_copies"] < book.issued_copies:
        errors["total_copies"] = (
            f"{book.issued_copies} copies are currently issued, so the total can't go lower."
        )
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    issued = book.issued_copies
    for field, value in cleaned.items():
        setattr(book, field, value)
    book.available_copies = book.total_copies - issued
    book.save()

    return JsonResponse({"book": book.to_dict()})


# --------------------------------------------------------- issue / return
@require_http_methods(["POST"])
def book_issue(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"errors": {"__all__": "That book is no longer in the catalogue."}}, status=404)

    if book.available_copies < 1:
        return JsonResponse({"errors": {"__all__": "Every copy is already issued."}}, status=400)

    book.available_copies -= 1
    book.save()
    return JsonResponse({"book": book.to_dict()})


@require_http_methods(["POST"])
def book_return(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"errors": {"__all__": "That book is no longer in the catalogue."}}, status=404)

    if book.available_copies >= book.total_copies:
        return JsonResponse({"errors": {"__all__": "No copies of this book are out."}}, status=400)

    book.available_copies += 1
    book.save()
    return JsonResponse({"book": book.to_dict()})


# ---------------------------------------------------------------- summary
@require_http_methods(["GET"])
def stats(request):
    agg = Book.objects.aggregate(
        copies=Sum("total_copies"), available=Sum("available_copies")
    )
    copies = agg["copies"] or 0
    available = agg["available"] or 0
    return JsonResponse(
        {
            "titles": Book.objects.count(),
            "copies": copies,
            "available": available,
            "issued": copies - available,
        }
    )
