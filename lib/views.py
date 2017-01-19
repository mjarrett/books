from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic

from lib.models import Book


# Create your views here.
def index(request):
    return HttpResponse("Here's where the main page of the family library will be")

def input(request):
    #return HttpResponse("Here's where input will go")
    return render(request, 'lib/input.html')
# def books(request):
#     all_books = [book.title for book in Book.objects.all() ]
#     context = {
#         'all_book_list':all_books,
#     }
#     return render(request, 'lib/index.html', context)

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
