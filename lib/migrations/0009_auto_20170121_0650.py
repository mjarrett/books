# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-21 06:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0008_auto_20170120_2311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='book',
        ),
        migrations.AddField(
            model_name='category',
            name='book',
            field=models.ManyToManyField(to='lib.Book'),
        ),
    ]