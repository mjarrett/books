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

def is_group_match(user1, user2):
    return any(x in user1.groups.all() for x in user2.groups.all())


def create_new_user():
    user = User.objects.create_user(username='mike',email='msjarrett@gmail.com',password='nitro666', first_name='Mike',last_name='Jarrett')
    group = Group.objects.get(name='hoy')
    user.groups.add(group)

    #Get a handle on a location
    #loc=...
    #connect user to location
    #user.location_set.add(loc)


# View functions
def index(request):
    return HttpResponse("Here's where the main page of the family library will be")


@login_required
def inputview(request,book_added=False):
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


@login_required
def addbook(request,isbn):
    grj = book_google_lookup('isbn:'+ isbn)
    b = Book(isbn=isbn,
            author=grj['items'][0]['volumeInfo']['authors'][0],
            title=grj['items'][0]['volumeInfo']['title'],
            thumbnail=grj['items'][0]['volumeInfo']['imageLinks']['thumbnail'],
            description=grj['items'][0]['volumeInfo']['description'],
            preview=grj['items'][0]['volumeInfo']['previewLink'],
            )
    b.save()

    user = request.user
    user.book_set.add(b)
    print(user)
    try:
        loc = user.location_set.get()
        loc.book_set.add(b)
    except:
        print("This user doesn't have a location")




    categories = grj['items'][0]['volumeInfo']['categories']
    for cat in categories:
        cat = cat.title() #ensure categories are in Title Case
        try: #try to get a handle on a category if it exists
            c = Category.objects.get(category=cat)
            b.category_set.add(c)
        except: # if it doesn't, make it
            #c = Category(category=cat)
            b.category_set.create(category=cat)

    return inputview(request,book_added=True)



@login_required
def booksview(request):
    object_list = Book.objects.all()
    #only return books if user in matching group
    object_list = [ b for b in object_list if is_group_match(b.owner,request.user) ]
    context = {'object_list':object_list}
    return render(request, 'lib/books.html', context)

@login_required
def bookview(request,pk):
    book = Book.objects.get(id=pk)
    if is_group_match(book.owner,request.user):
        context = {'book':book}
    else:
        context = {}
    return render(request, 'lib/book.html', context)

@login_required
def catview(request,pk):
    cat = Category.objects.get(id=pk)
    book_list = cat.book.all()
    book_list = [ b for b in book_list if is_group_match(b.owner,request.user)]
    context = {'book_list':book_list,'category':cat}
    return render(request, 'lib/genre.html', context)

@login_required
def catsview(request):
    object_list = Category.objects.all()
    object_list = [ (cat,len([ b for b in cat.book.all() if is_group_match(b.owner,request.user)])) for cat in object_list ]
    object_list = [ ob for ob in object_list if ob[1]>0]
    context = {'object_list':object_list}
    return render(request, 'lib/genres.html',context)

@login_required
def profile(request,username):
    if is_group_match(request.user,User.objects.get(username=username)):
        object_list = [ b for b in Book.objects.all() if b.owner.username == username]
        context = {'object_list':object_list,'user':username}
        return render(request, 'lib/profile.html', context)
    else:
        return HttpResponse("You do not have permission to view this page")

@login_required
def deletebook(request,pk):
    Book.objects.filter(id=pk).delete()
    return profile(request,request.user.username)

#View classes
# class BooksView(LoginRequiredMixin,generic.ListView):
#     model = Book
#     template_name = 'lib/books.html'

#
# class BookView(LoginRequiredMixin,generic.DetailView):
#     model = Book
#     template_name = 'lib/book.html'
