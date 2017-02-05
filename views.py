from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse


from django.contrib.auth.models import User, Group
from lib.models import Book, Category, Location, UserForm, GroupForm, EditBookForm, CommentForm

import group_codes
import requests
import json


from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from subprocess import Popen, PIPE

#Login and logout views handled automatically from urls.py

# Non-view helper functions
def send_mail(mailto,subject,body,html):
#def send_mail():
    #html = MIMEText("<html><head><title>Test Email</title></head><body>Some HTML</body>", "html")
    #msg = MIMEMultipart("alternative")

    #msg = MIMEText(body)
    msg = MIMEMultipart('alternative')

    msg["From"] = "library@mikejarrett.ca"
    msg["To"] = ", ".join(["msjarrett@gmail.com",mailto])
    msg["Subject"] = subject

    part1 = MIMEText(body)
    part2 = MIMETest(html)

    msg.attach(part1)
    msg.attach(part2)

    p = Popen(["/usr/bin/sendmail", "-t"], stdin=PIPE)
    p.communicate(msg.as_string())

def sort_by_attribute(object_list,att,rev):
    if rev=="True": rev=True
    elif rev=="False": rev=False
    if att == 'author':
        return sorted(object_list, key=lambda x: x.author.split()[-1], reverse=rev)
    elif att == 'owner':
        return sorted(object_list, key=lambda x: x.owner.username, reverse=rev)
    elif att == 'category':
        def catornone(obj):
            try:
                return obj.category.all()[0].category
            except:
                return ""
        return sorted(object_list, key=lambda x:catornone(x), reverse=rev)

    else:
        return sorted(object_list, key=lambda x: getattr(x,att), reverse=rev)

def book_google_lookup(query):
    url='https://www.googleapis.com/books/v1/volumes?q='+query
    google_response = requests.get(url)
    gr = google_response.text
    return json.loads(gr)

def is_group_match(user1, user2):
    return any(x in user1.groups.all() for x in user2.groups.all())

def sort_books(request, book_list):
    if request.method == 'GET' and  'att' in request.GET:
        att = request.GET.get('att')
        reverse = request.GET.get('reverse')
    else:
        att='id'
        reverse = True
    return sort_by_attribute(book_list,att,reverse)

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
        top_matches = grj['items'][0:25]
        context = {'matches':top_matches}
    else:
        context = {'matches':None}
    return render(request, 'lib/input.html',context)


@login_required
def addbook(request,googleid):
    grj = book_google_lookup('id:'+ googleid)
    volinfo = grj['items'][0]['volumeInfo']
    b = Book( title=volinfo['title'] )

    b.save()
    print(b)
    if 'authors' in volinfo:
        b.author = volinfo['authors'][0]
    else:
        b.author = "No Author"
    if 'imageLinks' in volinfo:
        b.thumbnail = volinfo['imageLinks']['thumbnail']
    if 'description' in volinfo:
        b.description = volinfo['description']
    if 'previewLink' in volinfo:
        b.preview = volinfo['previewLink']


    b.save()
    print(b, b.id)

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
    #only return books if user in matching group
    book_list = [ b for b in Book.objects.all() if is_group_match(b.owner,request.user) ]
    book_list = sort_books(request, book_list)
    context = {'book_list':book_list, 'subhead': 'All books available to you'}
    return render(request, 'lib/booksublist.html', context)

@login_required
def bookview(request,pk):
    book = Book.objects.get(id=pk)

    if request.method == 'POST' and 'commentsub' in request.POST:
        form = CommentForm(request.POST)
        comment = form.save(commit=False)
        comment.book = book
        comment.user = request.user
        comment.is_active = True
        comment.save()
        if request.POST.get('notifyowner', False):
            print('send email')
            body = '{} {} posted a comment about your book {} (http://apps.mikejarrett.ca{}):\n\n {} \n\n '.format(comment.user.first_name,comment.user.last_name,book.title, reverse('lib:book',args=(book.id,)),comment.text)
            html = '{} {} posted a comment about your book <a href="http://apps.mikejarrett.ca{}">{}</a>:\n\n {} \n\n '.format(comment.user.first_name,comment.user.last_name, reverse('lib:book',args=(book.id,)),book.title,comment.text)
            print(body)
            print(html)
            try:
                send_mail(book.owner.email, 'Someone commented on your book!',body,html)
                print('email sent successfully')
            except:
                print('email failed')
    catstring = ", ".join([ cat.category for cat in book.category.all() ])
    if is_group_match(book.owner,request.user):
        comments = book.comment_set.all()
        if book.owner == request.user:
            context = {'book':book, 'isowner':True, 'catstring':catstring, 'commentform':CommentForm(), 'comments':comments}
        else:
            context = {'book':book, 'isowner':False, 'catstring':catstring, 'commentform':CommentForm(), 'comments':comments}
    else:
        context = {}
    return render(request, 'lib/book.html', context)

@login_required
def editbookview(request,pk=None):


    # if we're catching a filled in form
    if request.method == 'POST' and 'editbooksub' in request.POST:
        if pk == None:
            book = Book(title='Title')
            book.save()
        else:
            book = Book.objects.get(id=pk)

        print(request.POST)
        if request.POST['title'] == "":
            request.POST['title'] = "No Title"
        f = EditBookForm(request.POST, instance=book)
        book = f.save(commit=False) #don't save book object till we've added categories
        if book.title == "":
            book.title = "No title"
            book.save()
        if book.author == "":
            book.author = "No author"
            book.save()
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
        return redirect('/lib/book/'+str(book.id))

    # if it's a fresh load
    else:
        if pk == None: #if we're making a new book
            form = EditBookForm(initial={'title':'Title', 'owner':request.user})
            book = None
        else: # if we're editing a saved book
            book = Book.objects.get(id=pk)
                # if user not allowed to edit book:
            if  request.user != book.owner:
                return render(request, 'lib/book.html', {'book':book})
            catstring = ", ".join([ cat.category for cat in book.category.all() ])
            form = EditBookForm(instance=book, initial={'formcategory':catstring})

        #filter the list of users in the dropdown menu, show first name+initial
        usergroups = [ group for group in request.user.groups.all() ]
        form.fields['owner'].queryset = User.objects.filter(groups__in=usergroups).distinct()
        form.fields['owner'].label_from_instance = lambda obj: "{} {}".format(obj.first_name, obj.last_name[0])

        return render(request, 'lib/editbook.html', {'book':book, 'form':form})

# @login_required
# def createbookview(request):
#     book = Book(owner=request.user, title='New Book')
#     book.save()
#     pk = book.id
#     context = {'book':book, 'form':EditBookForm(instance=book)}
#     return redirect('/lib/edit/'+str(pk))


@login_required
def authorview(request,authorname):
    book_list = [ b for b in Book.objects.filter(author=authorname) if is_group_match(b.owner,request.user)]
    book_list = sort_books(request, book_list)
    context = {'book_list':book_list, 'subhead': 'All book by {}'.format(authorname)}
    return render(request, 'lib/booksublist.html', context)


@login_required
def authorsview(request):
    authors = sorted(set(b.author for b in Book.objects.all()),key=lambda x: x.split()[-1])
    context = {'authors':authors}
    return render(request, 'lib/authors.html', context)

@login_required
def groupsview(request):
    object_list = [ group for group in request.user.groups.all() if group.name != request.user.username ]
    context = {'object_list':object_list}
    return render(request, 'lib/groups.html', context)



@login_required
def groupview(request,pk):

    group = Group.objects.get(id=pk)
    book_list = [book for book in Book.objects.all() if group in book.owner.groups.all()]
    book_list = sort_books(request, book_list)
    context = {'book_list':book_list, 'subhead': 'All books in group {}'.format(group.name)}
    return render(request, 'lib/booksublist.html', context)



@login_required
def catview(request,pk):
    cat = Category.objects.get(id=pk)
    book_list = [ b for b in cat.book.all() if is_group_match(b.owner,request.user)]
    book_list = sort_books(request, book_list)
    context = {'book_list':book_list, 'subhead': 'In genre {}'.format(cat.category)}
    return render(request, 'lib/booksublist.html', context)

@login_required
def catsview(request):
    object_list = Category.objects.all()
    object_list = [ (cat,len([ b for b in cat.book.all() if is_group_match(b.owner,request.user)])) for cat in object_list ]
    object_list = sorted([ ob for ob in object_list if ob[1]>0], key=lambda x:x[1], reverse=True)
    context = {'object_list':object_list}
    return render(request, 'lib/genres.html',context)

@login_required
def profile(request,username):
    profileuser = User.objects.get(username=username)
    #print(request.user.groups.all(), User.objects.get(username=username).groups.all())
    if is_group_match(request.user,profileuser):
        book_list = [ b for b in Book.objects.all() if b.owner.username == username]
        book_list = sort_books(request,book_list)
        context = {'book_list':book_list, 'subhead': 'Added by {} {}'.format(profileuser.first_name,profileuser.last_name[0])}
        return render(request, 'lib/booksublist.html', context)

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
            if request.POST['first_name'] == "" or request.POST['last_name'] == "":
                return render(request, 'lib/signup.html', {'form':UserForm(), 'error':"Please complete all fields!"})
            try:
                user = User.objects.create_user(username=request.POST['username'],email=request.POST['email'],password=request.POST['password'], first_name=request.POST['first_name'],last_name=request.POST['last_name'])
            except:
                return render(request, 'lib/signup.html', {'form':UserForm(), 'error':"Sorry, something didn't work. Please try again"})
            selfgroup = Group(name=request.POST['username'])
            selfgroup.save()
            selfgroup.user_set.add(user)
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            try:
                body =  'Username: {} \n Name: {} {} \n Email: {}'.format(user.username,user.first_name,user.last_name,user.email)
                send_mail('msjarrett@gmail.com','New User',body)

            except:
                print("Notification email failed")
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

def aboutview(request):
    return render(request,'lib/about.html')


#View classes
# class BooksView(LoginRequiredMixin,generic.ListView):
#     model = Book
#     template_name = 'lib/books.html'

#
# class BookView(LoginRequiredMixin,generic.DetailView):
#     model = Book
#     template_name = 'lib/book.html'
