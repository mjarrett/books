# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-19 00:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20170118_2355'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='questions',
            new_name='question',
        ),
    ]
