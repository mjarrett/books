from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from django.forms import Form, ModelForm, CharField, PasswordInput, BooleanField
from django.utils import timezone
# Create your models here.


class Location(models.Model):
    location = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='location')

    def __str__(self):
        return self.location

class Book(models.Model):

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='book')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book', null=True, blank=True)
    title = models.CharField(max_length=200, null=False, default='No Title', blank=False)
    isbn = models.IntegerField(default=None, null=True, blank=True)
    author = models.CharField(max_length=200,null=True, default='No author', blank=True)
    thumbnail = models.URLField(max_length=500,null=True, default=None, blank=True)
    description = models.TextField(max_length=3000,null=True, default=None, blank=True)
    preview = models.CharField(max_length=200,null=True, default=None, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if not self.title: return 'No title'
        else: return self.title

class Category(models.Model):
    category = models.CharField(max_length=200, unique=True)
    book = models.ManyToManyField(Book,related_name='category')

    def __str__(self):
        return self.category


class Comment(models.Model):
    text = models.TextField(max_length=2000)
    date_created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

# Model Forms
class UserForm(ModelForm):
    password = CharField(widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username','first_name','last_name','password','email']
        #help_texts = {'username': None}

class GroupForm(Form):
    groupcode = CharField(label='Group Code',max_length=100)

class EditBookForm(ModelForm):
    class Meta:
        model=Book
        fields = ['title','author','isbn','owner','description']
        #help_texts = {}
    formcategory = CharField(max_length=200, required=False)

class CommentForm(ModelForm):
    class Meta:
        model=Comment
        fields = ['text','notifyowner']
    notifyowner = BooleanField(required=False,initial=False)

# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
