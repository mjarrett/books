from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views


app_name = 'lib'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^input/$', views.inputview, name='input'),
    url(r'^addbook/(?P<isbn>\w+)/$',views.addbook,name='addbook'),
    url(r'^books/$', views.booksview, name='books'),
    url(r'^book/(?P<pk>[0-9]+)/$', views.bookview, name='book'),
    url(r'^delete/(?P<pk>[0-9]+)/$',views.deletebook,name='delete'),
    url(r'^genre/(?P<pk>[0-9]+)/$', views.catview, name='genre'),
    url(r'^genres/$', views.catsview, name='genres'),
    url(r'^user/(?P<username>\w+)/$', views.profile, name='profile'),
    url(r'^login/$', auth_views.login, {'template_name': 'lib/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'lib/logged_out.html'}, name='logout'),

    #url(r'^books/$', views.BooksView.as_view(), name='books'),
    #url(r'^book/(?P<pk>[0-9]+)/$', views.BookView.as_view(), name='book'),


    ]