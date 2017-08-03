from django.db import models
from datetime import datetime
from .article import Article
from authors.models.author import Author
from rest_framework import serializers
from django.contrib import admin
from django.template.defaultfilters import escape
from django.utils.html import format_html
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

    body = models.TextField(null=False, blank=False, max_length=500)
    # external_link = models.URLField(max_length=200)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=_DEFAULT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # raw_data = JSONField(null=True)

    # relations
    article = models.ForeignKey(Article, blank=False)
    author = models.ForeignKey(Author, null=False)


    def __str__(self):
        return '%s - %s' % (self.article.title, self.body[:100])


    class ContentSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        body = serializers.CharField(max_length=500)
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()


    class ContentAdmin(admin.ModelAdmin):
        date_hierarchy = 'created_at'
        list_display = ['id', 'link_to_article', 'link_to_author', 'body', 'content_type',]
        list_display_links = ('id',)
        search_fields = ('=article__title', 'article__slug', '^author__user__username')
        list_filter = ('status', 'created_at', )
        ordering = ['-created_at']
        # radio_fields = {"status": admin.VERTICAL}
        list_max_show_all = 10
        list_per_page = 10
        list_select_related = ('article', 'author', )
        
        # custom fields
        def content_type(self, obj):
            if obj.status == 1:
                return "Current"
            else:
                return "History"
        content_type.short_description = 'Type'


        def link_to_article(self, obj):
            return format_html('<a href="/admin/articles/article/%s/change/">%s</a>' % (obj.article.id, escape(obj.article.title)))
        link_to_article.short_description = "Article"


        def link_to_author(self, obj):
            return format_html('<a href="/admin/authors/author/%s/change/">%s</a>' % (obj.author.id, escape(obj.author.user.username)))
        link_to_author.short_description = "Author"


