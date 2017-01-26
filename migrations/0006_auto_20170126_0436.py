# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-26 04:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0005_auto_20170125_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='book', to='lib.Location'),
        ),
        migrations.AlterField(
            model_name='book',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='book', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='category',
            name='book',
            field=models.ManyToManyField(related_name='category', to='lib.Book'),
        ),
        migrations.AlterField(
            model_name='location',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location', to=settings.AUTH_USER_MODEL),
        ),
    ]