# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-09 12:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_auto_20170609_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=150, null=True, unique=True),
        ),
    ]
