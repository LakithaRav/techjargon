from django.db import models
from datetime import datetime
from rest_framework import serializers
from .article import Article
from authors.models.author import Author


# Create your models here.
class ArticleView(models.Model):

    class Meta:
        ordering = ['-created_at']


    ip_address = models.GenericIPAddressField(protocol='both', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated_at = models.DateTimeField(auto_now_add=True)

    # relations
    article = models.ForeignKey(Article, blank=False)
    author = models.ForeignKey(Author, blank=True, null=True)
