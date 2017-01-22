from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User, Group
from lib.models import Book, Category

import requests
import json

#Login and logout views handled automatically from urls.py

# Non-view helper functions
def book_google_lookup(query):
    url='https://www.googleapis.com/books/v1/volumes?q='+query
    google_response = requests.get(url)
    gr = google_response.text
    return json.loads(gr)


def create_new_user():
    user = User.objects.create_user(username='mike',email='msjarrett@gmail.com',password='nitro666', first_name='Mike',last_name='Jarrett')
    group = Group.objects.get(name='hoy')
    user.groups.add(group)

# View functions
def index(request):
    return HttpResponse("Here's where the main page of the family library will be")



@login_required
def addbook(request,isbn):
    username = request.user.username
    grj = book_google_lookup('isbn:'+ isbn)
    b = Book(owner=username,isbn=isbn,
            author=grj['items'][0]['volumeInfo']['authors'][0],
            title=grj['items'][0]['volumeInfo']['title'],
            )
    b.save()
    categories = grj['items'][0]['volumeInfo']['categories']
    for cat in categories:
        cat = cat.title() #ensure categories are in Title Case
        try: #try to get a handle on a category if it exists
            c = Category.objects.get(category=cat)
            b.category_set.add(c)
        except: # if it doesn't, make it
            #c = Category(category=cat)
            b.category_set.create(category=cat)

         #add category to book
    return input(request,book_added=True)

@login_required
def input(request,book_added=False):
    if book_added:
        context = {'added':True}
    elif 'book' in request.POST:
        new_book_title = request.POST['book']
        context = {'added_book':new_book_title}
        grj = book_google_lookup(new_book_title)
        top_matches = grj['items'][0:15]
        context = {'matches':top_matches}
    else:
        context = {'matches':None}
    return render(request, 'lib/input.html',context)



#View classes
class BooksView(LoginRequiredMixin,generic.ListView):
    model = Book
    template_name = 'lib/books.html'


class BookView(LoginRequiredMixin,generic.DetailView):
    model = Book
    template_name = 'lib/book.html'

class CatView(LoginRequiredMixin,generic.DetailView):
    model = Category
    template_name = 'lib/genre.html'

class CatsView(LoginRequiredMixin,generic.ListView):
    model = Category
    template_name = 'lib/genres.html'
