from django.db import models
from datetime import datetime
from .content import Content
from django.contrib.auth.models import User
from django.contrib import admin
from django.template.defaultfilters import escape
from django.utils.html import format_html

# Create your models here.
class ContentRating(models.Model):
    value = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # relations
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, null=False)

    class Meta:
    	ordering = ['id']

    
    class ContentRatingAdmin(admin.ModelAdmin):
        list_display = ['id', 'link_to_article', 'link_to_content', 'user', 'value', 'created_at',]
        list_display_links = ('id',)
        search_fields = ('^content__article__title', '^user__username')
        list_filter = ('value', 'created_at', )

        def link_to_article(self, obj):
            return format_html('<a href="/admin/articles/article/%s/change/">%s</a>' % (obj.content.article.id, escape(obj.content.article.title)))
        link_to_article.short_description = "Article"

        
        def link_to_content(self, obj):
            return format_html('<a href="/admin/articles/content/%s/change/">%s</a>' % (obj.content.id, escape(obj.content.id)))
        link_to_content.short_description = "Content"