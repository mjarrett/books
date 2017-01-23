from django.contrib import admin

# Register your models here.
from .models import Book, Category, Location
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Location)
