from django.conf.urls import url

from . import views

app_name = 'lib'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^input/$', views.input, name='input'),
    url(r'^books/$', views.BooksView.as_view(), name='books'),
    url(r'^book/(?P<pk>[0-9]+)/$', views.BookView.as_view(), name='book'),
    ]
