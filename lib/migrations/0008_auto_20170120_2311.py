# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 23:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0007_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]