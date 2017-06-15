from django.contrib import admin

# Register your models here.
from .models.article import Article
from .models.content import Content
from .models.tag import Tag
from .models.content_meta import ContentMeta

admin.site.register(Article)
admin.site.register(Content)
admin.site.register(Tag)
admin.site.register(ContentMeta)
