from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from .models import Book, Genre


def index(request, genre_id=None):
    genres = Genre.objects.all()

    search_content = request.GET.get('search', '')

    books_qs = Book.objects.all()

    if search_content:
        books_qs = books_qs.filter(Q(title__contains=search_content) |
                                    Q(author__contains=search_content))
    if genre_id:
        books_qs = books_qs.filter(genres__in=[genre_id])

    paginator = Paginator(books_qs, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'page_numbs': range(1, page_obj.paginator.num_pages + 1),
        'search_content': search_content,
        'genres': genres,
        'genre_id': genre_id,
    }

    return render(request, 'base.html', context=context)


def book_text(request, book_id):
    book = Book.objects.get(id=book_id)
    with open(book.text.path, 'r', encoding='UTF-8') as file:
        text = file.read()

    return render(request, 'book.html', {'book': book, 'text': text.split('\n')})
