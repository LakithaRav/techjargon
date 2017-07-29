from django.conf.urls import url

# from .views import tags
from . import apis

app_name = 'tags'

urlpatterns = [
    # apis
    url(r'^api/search/', apis.search, name='api_search'),
]
