from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login


from django.contrib.auth.models import User, Group
from lib.models import Book, Category, Location, UserForm, GroupForm, EditBookForm

import group_codes
import requests
import json

#Login and logout views handled automatically from urls.py

# Non-view helper functions
def sort_by_attribute(object_list,att,rev):
    if rev=="True": rev=True
    elif rev=="False": rev=False
    if att == 'author':
        return sorted(object_list, key=lambda x: x.author.split()[-1], reverse=rev)
    elif att == 'owner':
        return sorted(object_list, key=lambda x: x.owner.username, reverse=rev)
    elif att == 'category':
        return sorted(object_list, key=lambda x: list(x.category.all())[0].category, reverse=rev)
    else:
        return sorted(object_list, key=lambda x: getattr(x,att), reverse=rev)

def book_google_lookup(query):
    url='https://www.googleapis.com/books/v1/volumes?q='+query
    google_response = requests.get(url)
    gr = google_response.text
    return json.loads(gr)

def is_group_match(user1, user2):
    return any(x in user1.groups.all() for x in user2.groups.all())



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
    user.book.add(b)
    try:
        loc = user.location.get()
        loc.book.add(b)
    except:
        print("This user doesn't have a location")

    if 'categories' in grj['items'][0]['volumeInfo']:
        categories = grj['items'][0]['volumeInfo']['categories']
        for cat in categories:
            cat = cat.title() #ensure categories are in Title Case
            try: #try to get a handle on a category if it exists
                c = Category.objects.get(category=cat)
                b.category.add(c)
            except: # if it doesn't, make it
                #c = Category(category=cat)
                b.category.create(category=cat)

    return inputview(request,book_added=True)



@login_required
def booksview(request):
    object_list = Book.objects.all()
    #only return books if user in matching group
    object_list = [ b for b in object_list if is_group_match(b.owner,request.user) ]
    if request.method == 'GET' and  'att' in request.GET:
        att=request.GET.get('att')
        reverse = request.GET.get('reverse')
    else:
        att='id'
        reverse = True
    context = {'object_list':sort_by_attribute(object_list,att,reverse)}

    return render(request, 'lib/books.html', context)

@login_required
def bookview(request,pk):
    book = Book.objects.get(id=pk)
    catstring = ", ".join([ cat.category for cat in book.category.all() ])
    if is_group_match(book.owner,request.user):
        if book.owner == request.user:
            context = {'book':book, 'isowner':True, 'catstring':catstring}
        else:
            context = {'book':book, 'isowner':False, 'catstring':catstring}
    else:
        context = {}
    return render(request, 'lib/book.html', context)

@login_required
def editbookview(request,pk):
    book = Book.objects.get(id=pk)

    if request.method == 'POST' and 'editbooksub' in request.POST:
        f = EditBookForm(request.POST, instance=book)
        book = f.save(commit=False) #don't save book object till we've added categories

        book.category.clear() #clear categories in preparation for input
        catlist = request.POST['formcategory'].split(',')
        catlist = [ c.strip() for c in catlist]

        for cat in catlist:
            try:
                cat = Category.objects.get(category=cat)
                book.category.add(cat)
            except:
                book.category.create(category=cat)

        book.save()
        return render(request, 'lib/book.html', {'book':book})

    catstring = ", ".join([ cat.category for cat in book.category.all() ])
    form = EditBookForm(instance=book, initial={'formcategory':catstring})
    if request.user != book.owner:
        return render(request, 'lib/book.html', {'book':book})
    return render(request, 'lib/editbook.html', {'book':book, 'form':form})

@login_required
def createbookview(request):
    book = Book(owner=request.user)
    book.save()
    pk = book.id
    context = {'book':book, 'form':EditBookForm(instance=book)}
    return redirect('/lib/edit/'+str(pk))


@login_required
def authorview(request,authorname):
    book_list = Book.objects.filter(author=authorname)
    book_list = [ b for b in book_list if is_group_match(b.owner,request.user)]
    context = {'book_list':book_list,'author':authorname}
    return render(request, 'lib/author.html', context)

@login_required
def authorsview(request):
    authors = sorted(set(b.author for b in Book.objects.all()),key=lambda x: x.split()[-1])
    context = {'authors':authors}
    return render(request, 'lib/authors.html', context)

@login_required
def catview(request,pk):
    cat = Category.objects.get(id=pk)
    book_list = cat.book.all()
    book_list = [ b for b in book_list if is_group_match(b.owner,request.user)]
    #context = {'book_list':book_list,'category':cat}
    if request.method == 'GET' and  'att' in request.GET:
        att = request.GET.get('att')
        reverse = request.GET.get('reverse')
    else:
        att='id'
        reverse = False
    context = {'book_list':sort_by_attribute(book_list,att,reverse),'category':cat}
    return render(request, 'lib/genre.html', context)

@login_required
def catsview(request):
    object_list = Category.objects.all()
    object_list = [ (cat,len([ b for b in cat.book.all() if is_group_match(b.owner,request.user)])) for cat in object_list ]
    object_list = sorted([ ob for ob in object_list if ob[1]>0], key=lambda x:x[1], reverse=True)
    context = {'object_list':object_list}
    return render(request, 'lib/genres.html',context)

@login_required
def profile(request,username):

    #print(request.user.groups.all(), User.objects.get(username=username).groups.all())
    if is_group_match(request.user,User.objects.get(username=username)):
        object_list = [ b for b in Book.objects.all() if b.owner.username == username]

        if request.method == 'GET' and  'att' in request.GET:
            att = request.GET.get('att')
            reverse = request.GET.get('reverse')
        else:
            att='id'
            reverse = False
        context = {'object_list':sort_by_attribute(object_list,att,reverse), 'profileuser':username}

        return render(request, 'lib/profile.html', context)
    else:
        return HttpResponse("You do not have permission to view this page")

@login_required
def deletebook(request,pk):
    book = Book.objects.get(id=pk)
    if book.owner.username == request.user.username:
        book.delete()
        return profile(request,request.user.username)
    else:
        return profile(request,request.user.username)

def signup(request):
    if request.method == 'POST':
        if 'newusersub' in request.POST:
            form = UserForm(request.POST)
            if User.objects.filter(username=request.POST['username']).exists() or request.POST['username'] in group_codes.group_codes.values():
                return render(request, 'lib/signup.html', {'form':UserForm(), 'error':"Sorry, your user name is alread being used. Please try again"})
            try:
                user = User.objects.create_user(username=request.POST['username'],email=request.POST['email'],password=request.POST['password'], first_name=request.POST['first_name'],last_name=request.POST['last_name'])
            except:
                return render(request, 'lib/signup.html', {'form':UserForm(), 'error':"Sorry, something didn't work. Please try again"})
            selfgroup = Group(name=request.POST['username'])
            selfgroup.save()
            selfgroup.user_set.add(user)
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                return joingroup(request)
            else:
                print('login failed')
                return signup(request)

    context = {'form':UserForm()}
    return render(request, 'lib/signup.html',context)

@login_required
def joingroup(request):
    if request.method == 'POST' and  'groupcode' in request.POST:
        if request.POST['groupcode'] in group_codes.group_codes:
            groupname = group_codes.group_codes[request.POST['groupcode']]

            try:
                group = Group.objects.get(name=groupname)
            except:
                group = Group(name=groupname)
                group.save()

            group.user_set.add(request.user)


            context = {'success':groupname}
            return render(request, 'lib/joingroup.html',context)
        else:
            return render(request, 'lib/joingroup.html',{'form':GroupForm(),'error':"Sorry, that's not a valid group code. Try again or add a group later"})


    context = {'form':GroupForm()}
    return render(request, 'lib/joingroup.html',context)


#View classes
# class BooksView(LoginRequiredMixin,generic.ListView):
#     model = Book
#     template_name = 'lib/books.html'

#
# class BookView(LoginRequiredMixin,generic.DetailView):
#     model = Book
#     template_name = 'lib/book.html'
