# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-21 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0011_auto_20170121_0713'),
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