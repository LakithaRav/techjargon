from django.contrib import admin

# Register your models here.
from .models.author import Author

admin.site.register(Author)
