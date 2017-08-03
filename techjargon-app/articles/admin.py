from django.contrib import admin

# Register your models here.
from .models.article import Article
from .models.content import Content
from .models.content_meta import ContentMeta
from .models.content_rating import ContentRating

admin.site.register(Article, Article.ArticleAdmin)
admin.site.register(Content, Content.ContentAdmin)
admin.site.register(ContentMeta, ContentMeta.ContentMetaAdmin)
admin.site.register(ContentRating, ContentRating.ContentRatingAdmin)
