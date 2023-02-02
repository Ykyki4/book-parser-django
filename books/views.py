from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse

from .models import Book, Genre


def index(request):
    books = Book.objects.all()
    paginator = Paginator(books, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base.html', {'page_obj': page_obj, 'page_numbs': range(1, page_obj.paginator.num_pages+1)})


def book_text(request, id):
    book = Book.objects.get(id=id)
    with open(book.text.path, 'r', encoding='UTF-8') as file:
        text = file.read()

    return render(request, 'book.html', {'book': book, 'text': text.split('\n')})
