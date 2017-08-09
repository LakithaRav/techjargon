from django.db import models
from datetime import datetime
from tags.models.tag import Tag
from rest_framework import serializers
from django.contrib.contenttypes.fields import GenericRelation
from trackings.models.impression import Impression
import pdb
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import admin
from django.template.defaultfilters import escape
from django.utils.html import format_html

# Create your models here.
class Article(models.Model): 
    # choices
    STATUS = (
        (0, "Draft"),
        (1, "Published"),
    )
    _DEFAULT_STATUS = 1

    title = models.CharField(max_length=100, unique=True)
    status = models.PositiveSmallIntegerField(choices=STATUS, default=_DEFAULT_STATUS)
    slug = models.SlugField(unique=True, max_length=150)
    views = models.BigIntegerField(default=0)
    rating = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)
    in_home = models.BooleanField(default=False)


    # relations
    tags = models.ManyToManyField(Tag, related_name='%(class)s_tags')
    impressions = GenericRelation(Impression, related_query_name='articles')


    def __str__(self):
        return '%s' % self.title

    def active_content(self):
        content = None
        try:
            content = self.content_set.get(status=1)
        except ObjectDoesNotExist:
            content = None
        return content

    def history_content(self):
        return self.content_set.filter(status=0).order_by('-updated_at')

    def content_all(self):
        return self.content_set.order_by('-updated_at')

    def description_short(self):
        content = self.active_content()
        if content is not None:
            if len(content.body) > 150:
                return content.body[0:150] + "..."
            else:
                return content.body
        else:
            return ""

    def link(self):
        return "/article/" + self.slug

    def tags_str(self):
        return ', '.join([str(tag.name) for tag in self.tags.all()])


    class ArticleSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField(max_length=100)
        link = serializers.CharField(max_length=150)
        # rank = serializers.DecimalField(max_digits=6, decimal_places=2)
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        description_short = serializers.CharField(max_length=100)

    
    class ArticleAdmin(admin.ModelAdmin):
        date_hierarchy = 'created_at'
        list_display = ['title', 'views', 'rating', 'created_at', 'link_to_content', 'status', ]
        list_display_links = ('title',)
        list_editable = ('status',)
        search_fields = ('^title', 'tags__name')
        list_filter = ('tags', 'rating', 'status', 'created_at', )
        ordering = ['-created_at']
        # radio_fields = {"status": admin.VERTICAL}
        list_max_show_all = 10
        list_per_page = 10
        # list_select_related = ('tags', )
        # fieldsets = (
        #     (None, {
        #         'fields': ('title', 'slug', 'status')
        #     }),
        #     ('Advanced options', {
        #         'classes': ('collapse', 'wide'),
        #         'fields': ('tags',),
        #     }),
        # )
        filter_horizontal = ('tags',)
        exclude = ('views', 'rating')
        actions = ['make_published', 'make_show_in_home']

        def make_published(self, request, queryset):
            rows_updated = queryset.update(status=1)
            if rows_updated == 1:
                message_bit = "1 Article was"
            else:
                message_bit = "%s Articles were" % rows_updated
            self.message_user(request, "%s successfully marked as published." % message_bit)
        make_published.short_description = "Mark as published"

        def make_show_in_home(self, request, queryset):
            rows_updated = queryset.update(in_home=True)
            if rows_updated == 1:
                message_bit = "1 Article was"
            else:
                message_bit = "%s Articles were" % rows_updated
            self.message_user(request, "%s successfully marked as home Articles." % message_bit)
        make_show_in_home.short_description = "Mark as Home Article"

        def link_to_content(self, obj):
            return format_html('<a href="/admin/articles/content?q=%s">%s</a>' % (obj.title, escape(obj.content_set.count())))
        link_to_content.short_description = "Revisions"

