# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='body',
            field=models.TextField(),
        ),
    ]
