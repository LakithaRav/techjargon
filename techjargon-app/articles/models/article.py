from django.db import models
from datetime import datetime
from .tag import Tag
from rest_framework import serializers


# Create your models here.
class Article(models.Model):
    # choices
    STATUS = (
        (0, "Inactive"),
        (1, "Active"),
    )
    _DEFAULT_STATUS = 1

    title = models.CharField(max_length=100, unique=True)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=_DEFAULT_STATUS)
    slug = models.SlugField(unique=True, max_length=150)
    views = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # relations
    tags = models.ManyToManyField(Tag, related_name='%(class)s_tags')

    def __unicode__(self):
        return '%s' % self.title


    def active_content(self):
        content = self.content_set.get(status=1)
        return content

    def history_content(self):
        return self.content_set.filter(status=0).order_by('-updated_at')

    def content_all(self):
        return self.content_set.order_by('-updated_at')

    def description_short(self):
        content = self.content_set.get(status=1)
        if len(content.body) > 150:
            return content.body[0:150] + "..."
        else:
            return content.body

    def link(self):
        return "/article/" + self.slug

    def tags_str(self):
        return ', '.join([str(tag.name) for tag in self.tags.all()])


    class ArticleSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField(max_length=100)
        link = serializers.CharField(max_length=150)
        rank = serializers.DecimalField(max_digits=6, decimal_places=2)
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        description_short = serializers.CharField(max_length=100)
