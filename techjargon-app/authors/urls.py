from django.conf.urls import url

from . import views

app_name = 'authors'

urlpatterns = [
    url(r'^signin/', views.signin, name='signin'),
    url(r'^signout/', views.signout, name='signout'),
    url(r'^callback/', views.auth0_callback, name='callback'),
]
