# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-30 04:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0012_auto_20170130_0431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(blank=True, default='No author', max_length=200, null=True),
        ),
    ]
