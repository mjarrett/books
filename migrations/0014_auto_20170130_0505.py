# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-30 05:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0013_auto_20170130_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(default='No Title', max_length=200),
        ),
    ]