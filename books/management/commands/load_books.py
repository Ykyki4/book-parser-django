import sys
import time
from urllib.parse import urljoin, urlsplit

from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from django.core.files import File
from bs4 import BeautifulSoup
import requests
from requests import HTTPError

from books.models import Book, Genre


books = []


def check_for_redirect(response):
    if response.url == "https://tululu.org/":
        raise HTTPError


def parse_book(response, book_id):
    global books
    soup = BeautifulSoup(response.text, 'lxml')

    book_genres_tags_selector = 'span.d_book a'
    book_genres_tags = soup.select(book_genres_tags_selector)

    book_genres_raw = [book_genre.text for book_genre in book_genres_tags]
    book_genres_objects = []
    for book_genre in book_genres_raw:
        genre, created = Genre.objects.get_or_create(name=book_genre)
        book_genres_objects.append(genre)

    image_selector = 'div.bookimage img'
    image_select_result = soup.select_one(image_selector)

    image_url = urljoin(response.url, image_select_result['src'])
    image_response = requests.get(image_url)
    image_filename = urlsplit(image_url).path.split('/')[2]

    image_temp = NamedTemporaryFile()
    image_temp.write(image_response.content)
    image_temp.flush()

    heading_text_selector = 'table.tabs h1'
    heading_text_result = soup.select_one(heading_text_selector)

    title, author = heading_text_result.text.split("::")

    params = {"id": book_id}
    txt_url = f"https://tululu.org/txt.php"
    txt_response = requests.get(txt_url, params=params)
    txt_response.raise_for_status()
    check_for_redirect(txt_response)

    txt_temp = NamedTemporaryFile()
    txt_temp.write(txt_response.content)
    txt_temp.flush()

    book = Book(
        id=book_id,
        title=title.strip(),
        author=author.strip(),
        )

    book.text.save(
        f'{title.strip()} - {author.strip()}.txt',
        File(txt_temp),
        save=False,
    )

    if image_filename != 'nopic.gif':
        book.image.save(
            image_filename,
            File(image_temp),
            save=False,
        )

    book.genres_objects = book_genres_objects

    books.append(book)

    print(f'Книга {title.strip()} была добавлена в базу данных')


class Command(BaseCommand):
    help = 'load books category'

    def add_arguments(self, parser):
        parser.add_argument('start_id', type=int)
        parser.add_argument('end_id', type=int)

    def handle(self, *args, **options):
        for book_id in range(options['start_id'], options['end_id']):
            try:
                parse_url = f"https://tululu.org/b{book_id}/"
                response = requests.get(parse_url)
                response.raise_for_status()
                check_for_redirect(response)
                parse_book(response, book_id)

            except requests.exceptions.ConnectionError:
                print("Connection lost, next try in 1 minute", file=sys.stderr)
                time.sleep(60)

            except HTTPError:
                print("Книги не существует", file=sys.stderr)
                continue
        Book.objects.bulk_create(books)
        for book in books:
            genres_through = Book.genres.through
            genres_through.objects.bulk_create([
                genres_through(book_id=book.id, genre_id=genre.id)
                for genre in book.genres_objects
            ])
        self.stdout.write(self.style.SUCCESS('Книги были успешно добавлены в базу данных.'))
