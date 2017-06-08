from django.db import models
from datetime import datetime
from .article import Article
from authors.models.author import Author
from rest_framework import serializers
# from django.contrib.postgres.fields import JSONField


# Create your models here.
class Content(models.Model):

    class Meta:
        ordering = ['-updated_at']

    # choices
    STATUS = (
        (0, "Histroy"),
        (1, "Current"),
    )
    _DEFAULT_STATUS = 1

    body = models.TextField(null=False, blank=False)
    # external_link = models.URLField(max_length=200)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=_DEFAULT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # raw_data = JSONField(null=True)

    # relations
    article = models.ForeignKey(Article, blank=False)
    author = models.ForeignKey(Author, null=False)


    class ContentSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        body = serializers.CharField(max_length=500)
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()
