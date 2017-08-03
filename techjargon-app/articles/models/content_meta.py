from django.db import models
from datetime import datetime
from .content import Content
from django.contrib import admin
from django.template.defaultfilters import escape
from django.utils.html import format_html


# Create your models here.
class ContentMeta(models.Model):
    name = models.CharField(max_length=100)
    data = models.TextField(null=True)

    # relations
    content = models.ForeignKey(Content, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.content.article.title, self.name)

    class Meta:
    	ordering = ['id']

    class ContentMetaAdmin(admin.ModelAdmin):
        list_display = [ 'id', 'link_to_article', 'name', 'data',]
        list_display_links = ('id',)
        search_fields = ('^content__article__title',)
        list_filter = ('name', )
        list_max_show_all = 10
        list_per_page = 10
        list_select_related = ('content',)


        def link_to_article(self, obj):
            return format_html('<a href="/admin/articles/article/%s/change/">%s</a>' % (obj.content.article.id, escape(obj.content.article.title)))
        link_to_article.short_description = "Article"
