from django.conf.urls import url

from .views import article
from .views import tags
from . import apis

app_name = 'articles'

urlpatterns = [
    url(r'^$', article.index, name='index'),
    url(r'^new/', article.add, name='add'),
    url(r'^article/(?P<article_id>[0-9]+)/(?P<slug>[-\w\d]+)/update$', article.update, name='update'),
    url(r'^article/(?P<slug>[-\w\d]+)/$', article.detail, name='detail'),
    url(r'^article/(?P<slug>[-\w\d]+)/(?P<content_id>[0-9]+)/history$', article.history, name='history'),
    # apis
    url(r'^search/', apis.search, name='search'),
    url(r'^rate/', apis.rate, name='rate'),
    # tags
    url(r'^tags/(?P<slug>[-\w\d]+)/$', tags.detail, name='tags_detail'),
]
