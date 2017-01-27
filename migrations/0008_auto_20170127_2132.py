# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0007_book_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.CharField(default=None, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='preview',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='thumbnail',
            field=models.URLField(default=None, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]