from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.forms import Form, ModelForm, CharField, PasswordInput
# Create your models here.

class Location(models.Model):
    location = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='location')

    def __str__(self):
        return self.location

class Book(models.Model):

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name='book')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='book')
    title = models.CharField(max_length=200, null=True)
    isbn = models.IntegerField(default=-1)
    author = models.CharField(max_length=200,null=True)
    thumbnail = models.URLField(max_length=500,null=True)
    description = models.CharField(max_length=3000,null=True)
    preview = models.CharField(max_length=200,null=True)

    def __str__(self):
        if not self.title: return 'No title'
        else: return self.title

class Category(models.Model):
    category = models.CharField(max_length=200, unique=True)
    book = models.ManyToManyField(Book,related_name='category')

    def __str__(self):
        return self.category


# Model Forms
class UserForm(ModelForm):
    password = CharField(widget=PasswordInput())

    class Meta:
        model = User
        fields = ['username','first_name','last_name','password','email']
        help_texts = {'username': None}

class GroupForm(Form):
    groupcode = CharField(label='Group Code',max_length=100)

# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
