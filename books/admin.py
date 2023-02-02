from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from .models import Book, Genre


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    readonly_fields = ['id']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
