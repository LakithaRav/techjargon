# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-31 07:34
from __future__ import unicode_literals

from django.db import migrations

from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0017_auto_20170722_0625'),
    ]

    operations = [
        TrigramExtension(),
        UnaccentExtension(),
    ]
