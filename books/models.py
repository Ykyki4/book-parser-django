from django.db import models


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    author = models.CharField('Автор', max_length=100)
    image = models.ImageField('Обложка', upload_to='images', default='images/nopic.gif')
    text = models.FileField('Файл с текстом книги', upload_to='books_txt')
    genres = models.ManyToManyField(
        Genre,
        verbose_name='Жанры'
    )

    def __str__(self):
        return self.title

