from django.conf.urls import url

from . import views
from . import apis

app_name = 'articles'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/', views.add, name='add'),
    url(r'^article/(?P<article_id>[0-9]+)/(?P<slug>[-\w\d]+)/update$', views.update, name='update'),
    url(r'^article/(?P<slug>[-\w\d]+)/$', views.detail, name='detail'),
    url(r'^article/(?P<slug>[-\w\d]+)/(?P<content_id>[0-9]+)/history$', views.history, name='history'),
    url(r'^search/', apis.search, name='search'),
]
