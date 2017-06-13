# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 05:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0001_initial'),
        ('articles', '0009_auto_20170613_0519'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.BigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Content')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authors.Author')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
