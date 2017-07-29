from django.contrib import admin

# Register your models here.
from .models.tag import Tag

admin.site.register(Tag)