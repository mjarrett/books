from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from lib.models import Book
import requests
import json

# Create your views here.
def book_google_lookup(query):
    url='https://www.googleapis.com/books/v1/volumes?q='+query
    google_response = requests.get(url)
    gr = google_response.text
    return json.loads(gr)

def index(request):
    return HttpResponse("Here's where the main page of the family library will be")

def addbook(request,isbn):
    print(request)
    grj = book_google_lookup('isbn:'+ isbn)
    b = Book(isbn=isbn, author=grj['items'][0]['volumeInfo']['authors'][0],title=grj['items'][0]['volumeInfo']['title'])
    b.save()
    return BooksView.as_view()(request)

def input(request):
    #return HttpResponse("Here's where input will go")
    if 'book' in request.POST:
        new_book_title = request.POST['book']
        context = {'added_book':new_book_title}
        grj = book_google_lookup(new_book_title)
        top_matches = grj['items'][0:5]
        context = {'matches':top_matches}
        # b = Book(title=new_book_title)
        # b.save()
    else:
        context = {'matches':None}

    return render(request, 'lib/input.html',context)


class BooksView(generic.ListView):
    template_name = 'lib/index.html'
    #context_object_name = 'all_books_list'
    model = Book
    # def get_queryset(self):
    #     """Return list of all available books"""
    #     print([book.title for book in Book.objects.all()])
    #     return [book.title for book in Book.objects.all()]

# def book(request,book_id):
#     b = get_object_or_404(Book, pk=book_id)
#     return HttpResponse("This is a page for book {}".format(book_id))
class BookView(generic.DetailView):
    model = Book
    template_name = 'lib/book.html'
