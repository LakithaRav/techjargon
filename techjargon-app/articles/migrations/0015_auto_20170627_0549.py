# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 05:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0014_auto_20170627_0526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contentrating',
            name='owner',
        ),
        migrations.AddField(
            model_name='contentrating',
            name='user',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]